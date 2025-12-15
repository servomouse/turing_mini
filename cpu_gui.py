import tkinter as tk
from tkinter import ttk, scrolledtext
import math


def myhex(value: int) -> str:
    """Return a two‑digit hex string (e.g. 0x0A → '0A')."""
    return f"{value:02X}"


class CPUGUI:
    FONT = ("Consolas", 10)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CPU Emulator")
        self.cpu_state = "Stop"

        # -------------------------------------------------
        # Main layout: left = memory, right = registers
        # -------------------------------------------------
        main_pane = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ----- Memory viewer (ROM / RAM) -----
        mem_frame = ttk.Frame(main_pane)
        main_pane.add(mem_frame, weight=3)

        self.rom = self._create_memory_viewer(mem_frame, "ROM")
        self.ram = self._create_memory_viewer(mem_frame, "RAM")

        # ----- Register panel -----
        reg_frame = ttk.Frame(main_pane, padding=5)
        main_pane.add(reg_frame, weight=1)

        self._create_register_panel(reg_frame)

        # ----- Console area (tabbed) -----
        console_nb = ttk.Notebook(root)
        console_nb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.console1 = scrolledtext.ScrolledText(
            console_nb, height=6, wrap=tk.WORD, font=self.FONT
        )
        self.console2 = scrolledtext.ScrolledText(
            console_nb, height=6, wrap=tk.WORD, font=self.FONT
        )
        console_nb.add(self.console1, text="Console 1")
        console_nb.add(self.console2, text="Console 2")
        self.console1.insert(tk.END, "Console 1\n")
        self.console2.insert(tk.END, "Console 2\n")

        # Demo data
        self.populate_memory(self.rom, [i%256 for i in range(512)])
        self.populate_memory(self.ram, list(range(32)))

    # ----------------------------------------------------------------------
    # UI construction helpers
    # ----------------------------------------------------------------------
    def _create_memory_viewer(self, parent, label):
        """Return a dict with address/text widgets and read/write buttons."""
        frame = ttk.LabelFrame(parent, text=label, padding=5)
        frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=4)

        # ---- address and data text widgets ----
        addr = tk.Text(frame, width=9, height=10,
                    font=self.FONT, bg="#f0f0f0", wrap=tk.NONE)
        data = tk.Text(frame, width=48, height=10,
                    font=self.FONT, bg="#f8f8f8", wrap=tk.NONE)

        # ---- vertical scrollbar (shared) ----
        vbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        # connect both text widgets to the same scrollbar
        addr.config(yscrollcommand=vbar.set)
        data.config(yscrollcommand=vbar.set)
        vbar.config(command=lambda *args: (addr.yview(*args), data.yview(*args)))

        # pack the text widgets (they must be packed **before** the scrollbar
        # gets its size, otherwise the scrollbar will cover part of them)
        addr.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # ---- mouse‑wheel synchronization -----------------------------------
        def _on_mousewheel(event, source, partner):
            """Scroll both widgets together."""
            # Windows / macOS uses event.delta (120‑step); Linux uses button‑4/5.
            if event.num in (4, 5):          # Linux scroll events
                delta = 1 if event.num == 5 else -1
            else:                            # Windows / macOS
                delta = -1 * (event.delta // 120)

            # Apply the same delta to both widgets
            source.yview_scroll(delta, "units")
            partner.yview_scroll(delta, "units")
            return "break"   # prevent default single‑widget scrolling

        # Bind for all platforms
        addr.bind("<MouseWheel>", lambda e: _on_mousewheel(e, addr, data))
        data.bind("<MouseWheel>", lambda e: _on_mousewheel(e, data, addr))

        # Linux uses Button-4 (up) and Button-5 (down)
        addr.bind("<Button-4>", lambda e: _on_mousewheel(e, addr, data))
        addr.bind("<Button-5>", lambda e: _on_mousewheel(e, addr, data))
        data.bind("<Button-4>", lambda e: _on_mousewheel(e, data, addr))
        data.bind("<Button-5>", lambda e: _on_mousewheel(e, data, addr))

        # ---- button row (unchanged) ----
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=2)

        read_btn = ttk.Button(btn_row, text="Read",
                            command=lambda l=label: self.read_memory(l))
        read_btn.pack(side=tk.RIGHT, padx=2)

        write_btn = ttk.Button(btn_row, text="Write",
                            command=lambda l=label: self.write_memory(l))
        write_btn.pack(side=tk.RIGHT, padx=2)

        return {"addr": addr, "text": data,
                "read_btn": read_btn, "write_btn": write_btn}

    def _create_register_panel(self, parent):
        """Create the 9 register entries and control buttons."""
        reg_box = ttk.LabelFrame(parent, text="Registers", padding=5)
        reg_box.pack(fill=tk.BOTH, expand=True)

        self.registers = {}
        for i in range(9):
            lbl = ttk.Label(reg_box, text=f"R{i}:", width=3, anchor="e")
            lbl.grid(row=i, column=0, sticky="e", padx=2, pady=2)
            entry = ttk.Entry(reg_box, width=12, font=self.FONT)
            entry.grid(row=i, column=1, sticky="w", padx=2, pady=2)
            self.registers[f"R{i}"] = entry

        # control buttons
        btn_frame = ttk.Frame(reg_box)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=8)

        self.run_btn = ttk.Button(
            btn_frame, text="Run", width=10, command=self.run_btn_callback
        )
        self.run_btn.pack(side=tk.LEFT, padx=4)

        self.step_btn = ttk.Button(
            btn_frame, text="Step", width=10, command=self.step_btn_callback
        )
        self.step_btn.pack(side=tk.LEFT, padx=4)

        self.rst_btn = ttk.Button(
            btn_frame, text="Reset", width=10, command=self.rst_btn_callback
        )
        self.rst_btn.pack(side=tk.LEFT, padx=4)

    # ----------------------------------------------------------------------
    # Logic helpers
    # ----------------------------------------------------------------------
    def populate_memory(self, mem_space, image):
        """Fill address and data text widgets with hex values."""
        idx = 0
        rows = math.ceil(len(image) / 16)
        for i in range(rows):
            mem_space["addr"].insert(tk.END, f"0x{i:04X}:\n")
            line = []
            for _ in range(16):
                if idx < len(image):
                    line.append(myhex(image[idx]))
                else:
                    line.append("FF")
                idx += 1
            mem_space["text"].insert(tk.END, " ".join(line) + "\n")

    def read_memory(self, label):
        print(f"Read memory {label}")

    def write_memory(self, label):
        print(f"Write memory {label}")

    def run_btn_callback(self):
        if self.cpu_state == "Stop":
            self.cpu_state = "Run"
            self.run_btn.config(text="Stop")
        else:
            self.cpu_state = "Stop"
            self.run_btn.config(text="Run")
        print(f"CPU state: {self.cpu_state}")

    def rst_btn_callback(self):
        print("CPU reset")

    def step_btn_callback(self):
        print("CPU step")


if __name__ == "__main__":
    root = tk.Tk()
    CPUGUI(root)
    root.mainloop()
