import tkinter as tk
from tkinter import ttk, scrolledtext
import math


def myhex(value: int) -> str:
    """Return a two‑digit hex string (e.g. 0x0A → '0A')."""
    return f"{value:02X}"


# ----------------------------------------------------------------------
#  MemoryViewer – a self‑contained hex viewer with its own handlers
# ----------------------------------------------------------------------
class MemoryViewer:
    FONT = ("Consolas", 10)

    def __init__(self, parent, label, callbacks):
        """
        parent   – tk widget that will contain the viewer
        label    – "ROM" or "RAM"
        callbacks – dict with keys: read, write, load, save
                    each value is a callable that receives the label.
        """
        self.label = label
        self._build_ui(parent)
        self._bind_keys()
        # store callbacks for the four buttons
        self.read_cb = callbacks["read"]
        self.write_cb = callbacks["write"]
        self.load_cb = callbacks["load"]
        self.save_cb = callbacks["save"]

    # --------------------------------------------------------------
    #  UI construction
    # --------------------------------------------------------------
    def _build_ui(self, parent):
        frame = ttk.LabelFrame(parent, text=self.label, padding=5)
        frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=4)

        # ----- address and data text widgets -------------------------
        self.addr = tk.Text(frame, width=9, height=10,
                            font=self.FONT, bg="#f0f0f0", wrap=tk.NONE)
        self.data = tk.Text(frame, width=48, height=10,
                            font=self.FONT, bg="#f8f8f8", wrap=tk.NONE)

        # shared vertical scrollbar
        vbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.addr.config(yscrollcommand=vbar.set)
        self.data.config(yscrollcommand=vbar.set)
        vbar.config(command=lambda *a: (self.addr.yview(*a),
                                        self.data.yview(*a)))

        self.addr.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ----- button column (vertical) -----------------------------
        btn_col = ttk.Frame(frame)
        btn_col.pack(side=tk.RIGHT, fill=tk.Y, padx=4, pady=2)

        self.read_btn = ttk.Button(btn_col, text="Read",
                                   command=lambda: self.read_cb(self.label))
        self.write_btn = ttk.Button(btn_col, text="Write",
                                    command=lambda: self.write_cb(self.label))
        self.load_btn = ttk.Button(btn_col, text="Load",
                                   command=lambda: self.load_cb(self.label))
        self.save_btn = ttk.Button(btn_col, text="Save",
                                   command=lambda: self.save_cb(self.label))

        for b in (self.read_btn, self.write_btn, self.load_btn, self.save_btn):
            b.pack(fill=tk.X, pady=2)

    # --------------------------------------------------------------
    #  Keyboard handling (hex entry + custom navigation)
    # --------------------------------------------------------------
    def _bind_keys(self):
        # main handler – dispatches navigation vs. hex entry
        self.data.bind("<Key>", lambda e: self._hex_key_handler(e))

    # ----- helpers -------------------------------------------------
    @staticmethod
    def _is_hex_char(ch: str) -> bool:
        return ch.upper() in "0123456789ABCDEF"

    @staticmethod
    def _is_digit_column(col: int) -> bool:
        return col % 3 != 2          # every third column is a space

    # ----- navigation ------------------------------------------------
    def _hex_nav_handler(self, event):
        cur_line, cur_col = map(int, self.data.index(tk.INSERT).split("."))

        if event.keysym == "Left":
            new_col = cur_col - 1
            while new_col >= 0 and not self._is_digit_column(new_col):
                new_col -= 1
            new_col = max(new_col, 0)

        elif event.keysym == "Right":
            line_len = int(self.data.index(f"{cur_line}.end").split(".")[1])
            new_col = cur_col + 1
            while new_col < line_len and not self._is_digit_column(new_col):
                new_col += 1
            new_col = min(new_col, line_len)

        elif event.keysym == "Home":
            new_col = 0

        elif event.keysym == "End":
            line_len = int(self.data.index(f"{cur_line}.end").split(".")[1])
            new_col = line_len - 1
            while new_col >= 0 and not self._is_digit_column(new_col):
                new_col -= 1
            new_col = max(new_col, 0)

        elif event.keysym == "Up":
            if cur_line > 1:
                prev_line = cur_line - 1
                line_len = int(self.data.index(f"{prev_line}.end").split(".")[1])
                new_col = min(cur_col, line_len - 1)
                while new_col >= 0 and not self._is_digit_column(new_col):
                    new_col -= 1
                new_col = max(new_col, 0)
                cur_line = prev_line

        elif event.keysym == "Down":
            last_line = int(self.data.index(tk.END).split(".")[0]) - 1
            if cur_line < last_line:
                nxt_line = cur_line + 1
                line_len = int(self.data.index(f"{nxt_line}.end").split(".")[1])
                new_col = min(cur_col, line_len - 1)
                while new_col >= 0 and not self._is_digit_column(new_col):
                    new_col -= 1
                new_col = max(new_col, 0)
                cur_line = nxt_line

        else:
            return  # not a navigation key we handle

        self.data.mark_set(tk.INSERT, f"{cur_line}.{new_col}")
        return "break"

    # ----- hex‑character entry ------------------------------------
    def _hex_key_handler(self, event):
        # navigation keys → custom handler
        if event.keysym in {"Left", "Right", "Up", "Down", "Home", "End"}:
            return self._hex_nav_handler(event)

        # printable character handling
        ch = event.char
        if not ch or not self._is_hex_char(ch):
            return "break"

        cur_index = self.data.index(tk.INSERT)
        line, col = map(int, cur_index.split("."))
        replace_col = col
        replace_idx = f"{line}.{replace_col}"
        next_idx = f"{line}.{replace_col + 1}"

        self.data.delete(replace_idx, next_idx)
        self.data.insert(replace_idx, ch.upper())
        self.data.mark_set(tk.INSERT, f"{line}.{replace_col + 1}")
        return "break"

    # --------------------------------------------------------------
    #  Public helper – fill the viewer with a list of integers
    # --------------------------------------------------------------
    def populate_memory(self, image):
        """image – iterable of byte values (0‑255)."""
        self.addr.delete("1.0", tk.END)
        self.data.delete("1.0", tk.END)

        idx = 0
        rows = math.ceil(len(image) / 16)
        for i in range(rows):
            self.addr.insert(tk.END, f"0x{i:04X}:\n")
            line = []
            for _ in range(16):
                if idx < len(image):
                    line.append(f"{image[idx]:02X}")
                else:
                    line.append("FF")
                idx += 1
            self.data.insert(tk.END, " ".join(line) + "\n")



# ----------------------------------------------------------------------
#  TerminalApp – a self‑contained terminal with its own handlers
# ----------------------------------------------------------------------
class TerminalApp:
    def __init__(self, parent):
        self.parent = parent

        # Text widget to simulate terminal output/input
        self.console = scrolledtext.ScrolledText(self.parent, wrap='word', height=20, width=60)
        self.console.pack(side=tk.TOP)

        # Configure the console to be read-only before the prompt
        self.console.bind("<Key>", self.prevent_edit_before_prompt)

        # Disable mouse clicks to move the cursor
        self.console.bind("<Button-1>", self.prevent_mouse_movement)
        
        # Prompt
        self.prompt = ">>> "
        self.console.insert(tk.END, self.prompt)
        
        # Bind Enter and Tab keys
        self.console.bind("<Return>", self.on_enter)
        self.console.bind("<Tab>", self.on_tab)

        # Store the current position in the text widget
        self.current_position = tk.END
    
    def get_horizontal_position(self, coords):
        pos = int(coords.split('.')[1])
        return pos

    def prevent_edit_before_prompt(self, event):
        # Allow editing only after the prompt
        # print(f"{event.keysym = }")
        pos = self.get_horizontal_position(self.console.index(tk.INSERT))

        if event.keysym in ["Up", "Down"]:
            return "break"  # Do nothing
        if event.keysym in ["BackSpace", "Left"]:  # Backspace or arrow left
            if pos <= len(self.prompt):
                return "break"
        if pos < len(self.prompt):  # Prevent other keys before the prompt
            return "break"  # Prevent editing
    
    def prevent_mouse_movement(self, event):
        # Prevent moving the cursor with the mouse
        if self.console.focus_get() != self.console:
            self.console.focus_set()
        return "break"
        
    def on_enter(self, event):
        # Capture the input after the prompt
        user_input = self.console.get("end-1c linestart", "end-1c")
        if user_input:
            self.console.insert(tk.END, f"\nYou entered: {user_input}")
        self.write_to_console("")
        return "break"  # Prevent the default behavior

    def on_tab(self, event):
        user_input = self.console.get("end-1c linestart", "end-1c")
        if user_input:
            self.console.insert(tk.END, f"\nYou entered: {user_input}")
        self.write_to_console("")
        return "break"  # Prevent the default behavior

    def write_to_console(self, text):
        # Function to add text to the console
        self.console.insert(tk.END, f"{text}\n{self.prompt}")  # Add text and prompt
        self.console.mark_set(tk.INSERT, tk.END)  # Move cursor to the end


class CPUGUI:
    FONT = ("Consolas", 10)

    def __init__(self, root):
        self.root = root
        self.root.title("CPU Emulator")
        self.cpu_state = "Stop"

        # ---------- top area ----------
        top_frame = ttk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # memory viewers (ROM & RAM)
        mem_frame = ttk.Frame(top_frame)
        mem_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5)

        # callbacks dictionary passed to each viewer
        mem_cbs = {
            "read": self.read_memory,
            "write": self.write_memory,
            "load": self.load_memory,
            "save": self.save_memory,
        }

        self.rom = MemoryViewer(mem_frame, "ROM", mem_cbs)
        self.ram = MemoryViewer(mem_frame, "RAM", mem_cbs)

        # ---------- registers ----------
        regs_frame = ttk.LabelFrame(top_frame, text="Registers", padding=5)
        regs_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=9)

        self.registers = {}
        for i in range(9):
            lbl = ttk.Label(regs_frame, text=f"R{i}:", width=3, anchor="e")
            lbl.grid(row=i, column=0, sticky="e", padx=2, pady=2)
            entry = ttk.Entry(regs_frame, width=12, font=self.FONT)
            entry.grid(row=i, column=1, sticky="w", padx=2, pady=2)
            self.registers[f"R{i}"] = entry

        # control buttons (Run / Step / Reset)
        btn_box = ttk.Frame(regs_frame)
        btn_box.grid(row=9, column=0, columnspan=2, pady=8)

        self.run_btn = ttk.Button(btn_box, text="Run", width=10, command=self.run_btn_callback)
        self.run_btn.pack(side=tk.LEFT, padx=4)

        self.step_btn = ttk.Button(btn_box, text="Step", width=10, command=self.step_btn_callback)
        self.step_btn.pack(side=tk.LEFT, padx=4)

        self.rst_btn = ttk.Button(btn_box, text="Reset", width=10, command=self.rst_btn_callback)
        self.rst_btn.pack(side=tk.LEFT, padx=4)

        btn_box = ttk.Frame(regs_frame)
        btn_box.grid(row=9, column=0, columnspan=2, pady=8)

        cpu_status_text_label = ttk.Label(regs_frame, text="CPU state:", font =("Courier", 14))
        cpu_status_text_label.grid(row=10, column=0, columnspan=2, pady=4)

        self.cpu_status_label = ttk.Label(regs_frame, text="HALT", font =("Courier", 14), background="yellow")
        self.cpu_status_label.grid(row=11, column=0, columnspan=2, pady=4)

        # ---------- consoles (tabbed) ----------
        console_nb = ttk.Notebook(root)
        console_nb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.console1 = TerminalApp(console_nb)
        self.console2 = TerminalApp(console_nb)
        console_nb.add(self.console1.console, text="Console 1")
        console_nb.add(self.console2.console, text="Console 2")

        # ---------- demo data ----------
        self.rom.populate_memory([i for i in range(37)])
        self.ram.populate_memory([i for i in range(32)])

    # ------------------------------------------------------------------
    #  Dummy callbacks for the memory viewer buttons
    # ------------------------------------------------------------------
    def read_memory(self, label):
        print(f"[{label}] Read button pressed")

    def write_memory(self, label):
        print(f"[{label}] Write button pressed")

    def load_memory(self, label):
        print(f"[{label}] Load button pressed")

    def save_memory(self, label):
        print(f"[{label}] Save button pressed")

    # ------------------------------------------------------------------
    #  CPU control callbacks
    # ------------------------------------------------------------------
    def run_btn_callback(self):
        if self.cpu_state == "Stop":
            self.cpu_state = "Run"
            self.run_btn.config(text="Stop")
            self.step_btn.config(state="disabled")
            self.cpu_status_label.config(text = "RUNNING", background="green")
        else:
            self.cpu_state = "Stop"
            self.run_btn.config(text="Run")
            self.step_btn.config(state="enabled")
            self.cpu_status_label.config(text = "HALT", background="yellow")
        print(f"CPU state: {self.cpu_state}")

    def step_btn_callback(self):
        print("CPU step")

    def rst_btn_callback(self):
        print("CPU reset")
    
    # --------------------------------------------------------------------
    # Console methods
    # --------------------------------------------------------------------
    def print_to_console(self, console, message):
        """Print a message to the specified console."""
        console.insert(tk.END, message + "\n")
        console.see(tk.END)  # Scroll to the end to show the latest message

    def on_console1_enter(self, event):
        # Get all text from the console
        text = self.console1.get("1.0", tk.END).strip()
        # Split the text into lines and get the last line
        lines = text.splitlines()
        if lines:  # Check if there are any lines
            last_line = lines[-1]  # Get the last line
            print(f"Console 1: {last_line}")
        # self.console1.delete("1.0", tk.END)  # Clear console

    def on_console2_enter(self, event):
        # Get all text from the console
        text = self.console2.get("1.0", tk.END).strip()
        # Split the text into lines and get the last line
        lines = text.splitlines()
        if lines:  # Check if there are any lines
            last_line = lines[-1]  # Get the last line
            print(f"Console 1: {last_line}")
        # self.console2.delete("1.0", tk.END)  # Clear console

# def on_console1_enter(self, event):
#     text = self.console1.get("1.0", tk.END).strip()
#     if text:  # Only print if there is something to print
#         print(f"Console 1: {text}")
#         # self.console1.delete("1.0", tk.END)  # Clear console

# def on_console2_enter(self, event):
#     text = self.console2.get("1.0", tk.END).strip()
#     if text:  # Only print if there is something to print
#         print(f"Console 2: {text}")
#         # self.console2.delete("1.0", tk.END)  # Clear console


if __name__ == "__main__":
    root = tk.Tk()
    CPUGUI(root)
    root.mainloop()
