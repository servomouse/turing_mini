import tkinter as tk
from tkinter import scrolledtext

class CPUGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Emulator")

        # Top frame
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # ROM and RAM Frames
        self.memory_frame = tk.Frame(self.top_frame)
        self.memory_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5)

        # ROM control frame
        self.rom_ctrl_frame = tk.Frame(self.memory_frame)
        self.rom_ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        # ROM
        rom_label = tk.Label(self.rom_ctrl_frame, text="ROM")
        rom_label.pack(side=tk.LEFT, fill=tk.X)
        rom_write_btn = tk.Button(self.rom_ctrl_frame, text="Write", command=lambda: self.write_memory(0))
        rom_write_btn.pack(side=tk.RIGHT, fill=tk.X)
        rom_read_btn = tk.Button(self.rom_ctrl_frame, text="Read", command=lambda: self.read_memory(0))
        rom_read_btn.pack(side=tk.RIGHT, fill=tk.X)

        self.rom_text = tk.Text(self.memory_frame, height=10, width=60, wrap=tk.NONE)
        self.rom_text.pack(side=tk.TOP, fill=tk.X)
        # self.rom_text.grid(row=1, column=0, columnspan=3, sticky="ew")

        # RAM control frame
        self.ram_ctrl_frame = tk.Frame(self.memory_frame)
        self.ram_ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        # RAM
        ram_label = tk.Label(self.ram_ctrl_frame, text="RAM")
        ram_label.pack(side=tk.LEFT, fill=tk.X)
        ram_write_btn = tk.Button(self.ram_ctrl_frame, text="Write", command=lambda: self.write_memory(1))
        ram_write_btn.pack(side=tk.RIGHT, fill=tk.X)
        ram_read_btn = tk.Button(self.ram_ctrl_frame, text="Read", command=lambda: self.read_memory(1))
        ram_read_btn.pack(side=tk.RIGHT, fill=tk.X)

        self.ram_text = tk.Text(self.memory_frame, height=10, width=60, wrap=tk.NONE)
        self.ram_text.pack(side=tk.TOP, fill=tk.X)
        # self.ram_text.grid(row=3, column=0, columnspan=3, sticky="ew")

        # Register Fields
        self.registers_frame = tk.Frame(self.top_frame)
        self.registers_frame.pack(side=tk.RIGHT, padx=10, pady=5, anchor='n')

        self.registers = {}
        for i in range(9):
            label = f"R{i}:"
            lbl = tk.Label(self.registers_frame, text=label)
            lbl.grid(row=i, column=0)
            entry = tk.Entry(self.registers_frame, width=10)
            entry.grid(row=i, column=1)
            self.registers[label] = entry

        # Consoles
        self.console_frame = tk.Frame(root)
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.console1 = scrolledtext.ScrolledText(self.console_frame, height=5, wrap=tk.WORD)
        self.console1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.console1.insert(tk.END, "Console 1\n")

        self.console2 = scrolledtext.ScrolledText(self.console_frame, height=5, wrap=tk.WORD)
        self.console2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.console2.insert(tk.END, "Console 2\n")

        # Initialize some data for demo purposes
        self.populate_memory()

    def populate_memory(self):
        # Populate ROM and RAM with hexadecimal data for demonstration
        self.rom_text.insert(tk.END, "Address 00: 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n")
        self.ram_text.insert(tk.END, "Address 00: 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F\n")

    def read_memory(self, idx):
        print(f"Read memory {idx}")

    def write_memory(self, idx):
        print(f"Write memory {idx}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUGUI(root)
    root.mainloop()
