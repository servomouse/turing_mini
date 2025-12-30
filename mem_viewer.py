import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import copy


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
        self.buffer = None

    # --------------------------------------------------------------
    #  UI construction
    # --------------------------------------------------------------
    def _build_ui(self, parent):
        frame = ttk.LabelFrame(parent, text=self.label, padding=5)
        # Use fill=tk.BOTH and expand=True so it fills the PanedWindow pane
        frame.pack(fill=tk.BOTH, expand=True, pady=4)

        # ----- address and data text widgets -------------------------
        self.addr = tk.Text(frame, width=9, height=10,
                            font=self.FONT, bg="#f0f0f0", wrap=tk.NONE)
        self.data = tk.Text(frame, width=48, height=10,
                            font=self.FONT, bg="#f8f8f8", wrap=tk.NONE)
        self.data.tag_config("modified", foreground="red")

        # shared vertical scrollbar
        vbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.addr.config(yscrollcommand=vbar.set)
        self.data.config(yscrollcommand=vbar.set)
        vbar.config(command=lambda *a: (self.addr.yview(*a),
                                        self.data.yview(*a)))

        self.addr.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mousewheel for both widgets
        self.data.bind("<MouseWheel>", self._on_mousewheel)
        self.addr.bind("<MouseWheel>", self._on_mousewheel)

        self.data.bind("<ButtonRelease-1>", self._on_click_snap)

        # ----- button column (vertical) -----------------------------
        btn_col = ttk.Frame(frame)
        btn_col.pack(side=tk.RIGHT, fill=tk.Y, padx=4, pady=2)

        self.read_btn = ttk.Button(btn_col, text="Read",
                                   command=lambda: self.read_cb(self.label))
        self.write_btn = ttk.Button(btn_col, text="Write",
                                    command=self.mem_write_btn_cb)
        self.load_btn = ttk.Button(btn_col, text="Load",
                                   command=lambda: self.load_cb(self.label))
        self.save_btn = ttk.Button(btn_col, text="Save",
                                   command=lambda: self.save_cb(self.label))

        for b in (self.read_btn, self.write_btn, self.load_btn, self.save_btn):
            b.pack(fill=tk.X, pady=2)
    
    def mem_write_btn_cb(self):
        self.data.tag_remove("modified", "1.0", tk.END)
        self.write_cb(self.label)
    
    def _sync_scroll(self, *args):
        """Moves both text widgets when the scrollbar is dragged."""
        self.addr.yview(*args)
        self.data.yview(*args)

    def _on_mousewheel(self, event):
        """Synchronizes scrolling when using the mouse wheel."""
        if event.num == 4 or event.delta > 0:
            move = -1
        else:
            move = 1
        self.addr.yview_scroll(move, "units")
        self.data.yview_scroll(move, "units")
        return "break"
    
    def _on_click_snap(self, event):
        """Prevents the cursor from landing on the space columns."""
        cur_index = self.data.index(tk.INSERT)
        line, col = map(int, cur_index.split("."))
        line_len = int(self.data.index(f"{line}.end").split(".")[1])

        # Check if we are on a prohibited space (2, 5, 8...)
        if not self._is_digit_column(col):
            # 1. Try moving to the next position (n+1)
            new_col = col + 1
            
            if new_col < line_len:
                # Target is within the same line
                self.data.mark_set(tk.INSERT, f"{line}.{new_col}")
            else:
                # 2. At end of line, try 0th position of next line
                next_line = line + 1
                last_line = int(self.data.index(tk.END).split(".")[0]) - 1
                
                if next_line <= last_line:
                    self.data.mark_set(tk.INSERT, f"{next_line}.0")
                else:
                    # 3. No next line exists, snap back to n-1
                    self.data.mark_set(tk.INSERT, f"{line}.{col - 1}")
        
        # Ensure the address field stays synced after the click
        self._ensure_cursor_visible()

    # --------------------------------------------------------------
    #  Keyboard handling (hex entry + custom navigation)
    # --------------------------------------------------------------
    def _bind_keys(self):
        # main handler – dispatches navigation vs. hex entry
        self.data.bind("<Key>", lambda e: self._hex_key_handler(e))
        self.data.bind("<Control-g>", self._show_goto_popup)

    # ----- helpers -------------------------------------------------
    @staticmethod
    def _is_hex_char(ch: str) -> bool:
        return ch.upper() in "0123456789ABCDEF"

    @staticmethod
    def _is_digit_column(col: int) -> bool:
        return col % 3 != 2          # every third column is a space

    # ----- navigation ------------------------------------------------
    def _show_goto_popup(self, event=None):
        """Creates a modal popup window for address entry."""
        popup = tk.Toplevel(self.data)
        popup.title("Go to Address")
        popup.geometry("250x120")
        popup.resizable(False, False)
        
        # Make it modal (intercepts events to the main window)
        popup.transient(self.data)
        popup.grab_set()

        ttk.Label(popup, text="Enter Hex Address (e.g. 0x1A0):").pack(pady=5)
        
        entry = ttk.Entry(popup)
        entry.pack(pady=5, padx=10, fill=tk.X)
        entry.focus_set()

        def do_jump(event=None):
            addr_str = entry.get().strip()
            try:
                # Handle both '0x' prefix and raw hex
                target_addr = int(addr_str, 16) if 'x' in addr_str.lower() else int(addr_str, 16)
                
                # Calculate line (16 bytes per row)
                # Row 0 is line 1 in Tkinter Text widgets
                target_line = (target_addr // 16) + 1
                
                # Verify bounds
                last_line = int(self.data.index(tk.END).split(".")[0]) - 1
                if 1 <= target_line <= last_line:
                    # Move cursor and scroll
                    self.data.mark_set(tk.INSERT, f"{target_line}.0")
                    self._ensure_cursor_visible()
                    popup.destroy()
                else:
                    from tkinter import messagebox
                    messagebox.showwarning("Out of Bounds", f"Address 0x{target_addr:X} is outside memory range.")
            except ValueError:
                from tkinter import messagebox
                messagebox.showerror("Invalid Input", "Please enter a valid hexadecimal value.")

        btn = ttk.Button(popup, text="Go", command=do_jump)
        btn.pack(pady=5)
        
        # Allow pressing 'Enter' to submit
        entry.bind("<Return>", do_jump)
        # Allow 'Esc' to close
        popup.bind("<Escape>", lambda e: popup.destroy())

        return "break"

    def _ensure_cursor_visible(self):
        """Scrolls the view so the cursor is always visible with a 1-line margin."""
        # Get current cursor position
        cur_index = self.data.index(tk.INSERT)
        line, _ = map(int, cur_index.split("."))
        
        # Calculate neighbors for padding
        prev_line = max(1, line - 1)
        next_line = line + 1  # Text widget handles out-of-bounds gracefully
        
        # Make data see the lines, then sync address to data
        # We check next_line first so that moving down feels natural
        self.data.see(f"{next_line}.0")
        self.data.see(f"{prev_line}.0")
        
        # Synchronize the address view to match the data view exactly
        self.addr.yview_moveto(self.data.yview()[0])

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
            else:
                new_col = cur_col

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
                new_col = cur_col

        else:
            return  # not a navigation key we handle

        self.data.mark_set(tk.INSERT, f"{cur_line}.{new_col}")
        self._ensure_cursor_visible()
        return "break"

    def update_buffer(self, offset, idx, subidx, new_value):
        orig_value = self.buffer[16*offset+idx]
        if subidx == 0:
            new_value = (orig_value & 0x0F) | (new_value << 4)
        else:
            new_value = (orig_value & 0xF0) | new_value
        print(f"{hex(orig_value) = }, {hex(new_value) = }")
        self.buffer[16*offset+idx] = new_value

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
        self.update_buffer(offset=line-1, idx=col//3, subidx=col%3, new_value=int(ch.upper(), base=16))
        replace_col = col
        replace_idx = f"{line}.{replace_col}"
        next_idx = f"{line}.{replace_col + 1}"

        self.data.delete(replace_idx, next_idx)
        self.data.insert(replace_idx, ch.upper(), "modified")
        new_line = False
        if replace_col >= 46:
            line += 1
            replace_col = 0
            new_line = True
        else:
            if (replace_col+2) % 3 == 0:
                self.data.delete(f"{line}.{replace_col+1}", f"{line}.{replace_col+2}")
                self.data.insert(f"{line}.{replace_col+1}", ' ')
                replace_col += 2
            else:
                replace_col += 1
        self.data.mark_set(tk.INSERT, f"{line}.{replace_col}")
        cur_index = self.data.index(tk.INSERT)
        if new_line and (cur_index != f"{line}.{replace_col}"):
            self.data.insert(tk.END, f"\n")
        cur_index = self.data.index(tk.INSERT)
        
        addr_index = self.addr.index(tk.INSERT)  # self.addr.insert(tk.END, f"0x{i:04X}:\n")
        addr_line, addr_col = map(int, addr_index.split("."))
        if line >= addr_line:
            self.addr.insert(tk.END, f"0x{line-1:04X}:\n")
        self._ensure_cursor_visible()
        return "break"
    
    def clear_modified_flag(self):
        """Removes the red color from all text."""
        self.data.tag_remove("modified", "1.0", tk.END)

    def show_buffer(self):
        idx = 0
        rows = math.ceil(len(self.buffer) / 16)
        self.addr.config(state=tk.NORMAL)
        for i in range(rows):
            self.addr.insert(tk.END, f"0x{i:04X}:\n")
            line = []
            for _ in range(16):
                if idx < len(self.buffer):
                    line.append(f"{self.buffer[idx]:02X}")
                else:
                    line.append("FF")
                idx += 1
            self.data.insert(tk.END, " ".join(line) + "\n")
        self.addr.config(state=tk.DISABLED)

    # --------------------------------------------------------------
    #  Public helper – fill the viewer with a list of integers
    # --------------------------------------------------------------
    def populate_memory(self, image):
        """image – iterable of byte values (0‑255)."""
        self.addr.delete("1.0", tk.END)
        self.data.delete("1.0", tk.END)
        self.buffer = copy.copy(image)
        self.show_buffer()


class CPUGUI:
    FONT = ("Consolas", 10)

    def __init__(self, root):
        self.root = root
        self.root.title("CPU Emulator")
        self.cpu_state = "Stop"# ---------- top area ----------
        top_frame = ttk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 1. Create a PanedWindow instead of a simple Frame
        # orient=tk.VERTICAL means the sash moves up and down
        # self.paned = ttk.Panedwindow(top_frame, orient=tk.VERTICAL)
        # self.paned.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.paned = tk.PanedWindow(top_frame, orient=tk.VERTICAL, 
                            sashwidth=5, sashrelief=tk.RAISED, 
                            bg="#d0d0d0")
        self.paned.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        # This adds a 1-pixel border around the sash elements
        style.configure("Vertical.TPanedwindow", background="#108010")

        mem_cbs = {
            "read": self.read_memory,
            "write": self.write_memory,
            "load": self.load_memory,
            "save": self.save_memory,
        }

        # 2. Create the containers for the viewers
        # We create them as children of the paned window
        rom_container = ttk.Frame(self.paned)
        ram_container = ttk.Frame(self.paned)

        # 3. Add them to the PanedWindow
        self.paned.add(rom_container)
        self.paned.add(ram_container)

        self.rom = MemoryViewer(rom_container, "ROM", mem_cbs)
        self.ram = MemoryViewer(ram_container, "RAM", mem_cbs)

        # ---------- demo data ----------
        self.rom.populate_memory([i%256 for i in range(1024)])
        self.ram.populate_memory([i%256 for i in range(1024)])

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


if __name__ == "__main__":
    root = tk.Tk()
    CPUGUI(root)
    root.mainloop()