from pynput import keyboard # pip install pynput
from queue import Queue
import threading
import time
import sys

class UserInputGetter:
    def __init__(self):
        self.input_queue = Queue()
        self.part_input = ""    # Contains user input before they hit Enter
        self.command = None     # Contains user input after user hit Enter, become None after read
        self.event = threading.Event()  # Set when user hit Enter, can be used for smart wait
        self.listener = keyboard.Listener(on_press=self.key_press)
        self.listener.start()

    def get_part_input(self):
        return self.part_input

    def get_command(self):
        cmd = self.command
        self.command = None
        self.event.clear()
        return cmd

    def key_press(self, key):
        if key == keyboard.Key.enter:
            self.command = self.part_input
            self.part_input = ""
            self.event.set()
        elif key == keyboard.Key.backspace:
            self.part_input = self.part_input[:-1]
        elif key == keyboard.Key.space:
            self.part_input += " "
        elif hasattr(key, 'char'):
            self.part_input += key.char


class Logger:
    def __init__(self, ui_getter, print_to_file=False):
        self.ui_getter = ui_getter
        self.print_to_file = print_to_file

    def print(self, filename, logstring):
        if self.print_to_file:
            with open(filename, 'a') as f:
                f.write(logstring + "\n")
        else:
            self.print_line(logstring)

    def print_line(self, line):
        part_cmd = self.ui_getter.get_part_input()
        print(f"\033[2K\r{line}")
        print(f"Enter command: {part_cmd}", end = "")
        sys.stdout.flush()


class CPURegs:
    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.E1 = 0
        self.E2 = 0
        self.PC = 0
        self.SP = 0
    
    @property
    def E0(self):
        return (self.A << 8) +(self.B << 4) + self.C
    
    @E0.setter
    def E0(self, value):
        self.A = (value >> 8) & 0x0F
        self.B = (value >> 4) & 0x0F
        self.C = value & 0x0F


class CPU:
    def __init__(self, binary=[], logger=None):
        self.RESET_VECTOR = [0xFF9, 0xFFC]
        self.ROM = binary
        self.RAM = [0 for _ in range(0x1000)]
        self.logger = logger
        self.regs = CPURegs()
        self.regs.PC = self.get_12b_value(self.ROM, self.RESET_VECTOR[0])
        self.regs.SP = self.get_12b_value(self.ROM, self.RESET_VECTOR[1])
    
    def get_12b_value(self, mem_space, address):
        return (mem_space[address] << 8) + (mem_space[address+1] << 4) + mem_space[address+2]
    
    def set_12b_value(self, mem_space, address, value):
        mem_space[address]   = (value >> 8) & 0x0F
        mem_space[address+1] = (value >> 4) & 0x0F
        mem_space[address+2] = value & 0x0F
    
    def get_8b_value(self, mem_space, address):
        return (mem_space[address] << 4) + mem_space[address+1]
    
    def set_8b_value(self, mem_space, address, value):
        mem_space[address]   = (value >> 4) & 0x0F
        mem_space[address+1] = value & 0x0F


def main():
    ui_getter = UserInputGetter()
    logger = Logger(ui_getter)
    cpu = CPU(binary=[], logger=logger)
    last_update = time.time()
    inner_state = 'stopped'
    while True:
        command = ui_getter.get_command()

        if command is not None:
            logger.print_line(f"User command from thread: {command}")
            if command == 'run':
                inner_state = 'running'
            elif command == 'print value':
                logger.print_line("Here is the value!")
            elif command == 'stop':
                inner_state = 'stopped'
            elif command == 'step':
                cpu.tick()
                inner_state = 'stopped'
            elif command == 'quit':
                return

        if inner_state == 'running':
            if time.time()-last_update > 0.1:
                if 0 == cpu.tick():
                    inner_state = 'stopped'
                last_update = time.time()
        elif inner_state == 'stopped':
            logger.print_line("The thread is stopped")
            ui_getter.event.wait()


if __name__ == "__main__":
    main()
