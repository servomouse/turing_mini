import tkinter as tk
from cpu_gui import CPUGUI
from dll_wrapper import DeviceLibraryWrapper
import time


if __name__ == "__main__":
    device = DeviceLibraryWrapper("bin/executables/libtest_clock_dll.dll")

    device.init()
    device.step()
    device.step()
    device.step()
    device.step()

    my_data = b'\xAA\xBB\xCC\xDD'
    device.mem_write(0x1, 0x10, my_data)
    result = device.mem_read(0x1, 0x10, 4)
    print(f"Memory read result: {result}")

    device.set_register(dev_id=0, reg_id=5, value=17)
    reg_val = device.get_register(dev_id=0, reg_id=5)
    print(f"Register Value: {reg_val}")

    device.run()
    time.sleep(5)
    device.stop()

    root = tk.Tk()
    CPUGUI(root)
    root.mainloop()