import tkinter as tk
from tkinter import scrolledtext
import math


def myhex(value):
    temp = hex(value)
    temp.replace("0x", "")
    if len(temp) == 1:
        temp = "0" + temp
    return temp

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

        self.rom = self.create_memory_viewer(self.memory_frame, "ROM")
        self.ram = self.create_memory_viewer(self.memory_frame, "RAM")

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
        self.populate_memory(self.rom, [i for i in range(37)])
        self.populate_memory(self.ram, [i for i in range(32)])
    
    def create_memory_viewer(self, memory_frame, label):
        mem_ctrl_frame = tk.Frame(memory_frame)
        mem_ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        mem_label = tk.Label(mem_ctrl_frame, text=label)
        mem_label.pack(side=tk.LEFT, fill=tk.X)

        mem_write_btn = tk.Button(mem_ctrl_frame, text="Write")
        mem_write_btn.pack(side=tk.RIGHT, fill=tk.X)

        mem_read_btn = tk.Button(mem_ctrl_frame, text="Read")
        mem_read_btn.pack(side=tk.RIGHT, fill=tk.X)

        mem_view_frame = tk.Frame(memory_frame)
        mem_view_frame.pack(side=tk.TOP, fill=tk.X)

        addr = tk.Text(mem_view_frame, height=10, width=9, wrap=tk.NONE)
        addr.pack(side=tk.LEFT, fill=tk.X)

        text = tk.Text(mem_view_frame, height=10, width=48, wrap=tk.NONE)
        text.pack(side=tk.LEFT, fill=tk.X)

        return {
            "addr": addr,
            "text": text,
            "read_btn": mem_read_btn,
            "write_btn": mem_write_btn
        }

    def populate_memory(self, mem_space, image):
        # Populate ROM and RAM with hexadecimal data for demonstration
        idx = 0
        for i in range(0, math.ceil(len(image) / 16)):
            mem_space["addr"].insert(tk.END, f"0x{i:04X}:\n")
            temp = []
            for j in range(16):
                if idx < len(image):
                    temp.append(f"{image[idx]:02X}")
                else:
                    temp.append("FF")
                idx += 1
            mem_space["text"].insert(tk.END, " ".join(temp) + "\n")

    def read_memory(self, idx):
        print(f"Read memory {idx}")

    def write_memory(self, idx):
        print(f"Write memory {idx}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUGUI(root)
    root.mainloop()
