import ctypes
import os

class DeviceLibraryWrapper:
    def __init__(self, dll_path):
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Could not find DLL at {dll_path}")

        self.lib = ctypes.CDLL(dll_path)
        self._setup_prototypes()

    def _setup_prototypes(self):
        """Define argument and return types for the DLL functions."""

        self.lib.init.argtypes = []
        self.lib.init.restype = None
        
        self.lib.run.argtypes = []
        self.lib.run.restype = None
        
        self.lib.stop.argtypes = []
        self.lib.stop.restype = None
        
        self.lib.reset.argtypes = []
        self.lib.reset.restype = None

        self.lib.save_state.argtypes = [ctypes.c_char_p]
        self.lib.save_state.restype = None
        
        self.lib.restore_state.argtypes = [ctypes.c_char_p]
        self.lib.restore_state.restype = None

        self.lib.step.argtypes = [ctypes.c_uint32]
        self.lib.step.restype = None

        self.lib.mem_write.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
        self.lib.mem_write.restype = None
        
        self.lib.mem_read.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
        self.lib.mem_read.restype = None

        # Register Access
        self.lib.set_register.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        self.lib.set_register.restype = None
        
        # get_register uses a pointer for the return value
        self.lib.get_register.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        self.lib.get_register.restype = None

    def init(self):
        self.lib.init()

    def save_state(self, filename: str):
        self.lib.save_state(filename.encode('utf-8'))

    def restore_state(self, filename: str):
        self.lib.restore_state(filename.encode('utf-8'))

    def run(self):
        self.lib.run()

    def stop(self):
        self.lib.stop()

    def step(self, num_steps: int):
        self.lib.step(num_steps)

    def reset(self):
        self.lib.reset()

    def mem_write(self, memspace: int, offset: int, data: bytes):
        # Convert python bytes to a ctypes array
        data_len = len(data)
        c_data = (ctypes.c_uint8 * data_len)(*data)
        self.lib.mem_write(memspace, offset, data_len, c_data)

    def mem_read(self, memspace: int, offset: int, length: int) -> bytes:
        # Create a buffer to receive data
        buffer = (ctypes.c_uint8 * length)()
        self.lib.mem_read(memspace, offset, length, buffer)
        return bytes(buffer)

    def set_register(self, dev_id: int, reg_id: int, value: int):
        self.lib.set_register(dev_id, reg_id, value)

    def get_register(self, dev_id: int, reg_id: int) -> int:
        value = ctypes.c_uint32()
        self.lib.get_register(dev_id, reg_id, ctypes.byref(value))
        return value.value



device = DeviceLibraryWrapper("bin/executables/libtest_clock_dll.dll")

device.init()
device.run()

my_data = b'\xAA\xBB\xCC\xDD'
device.mem_write(0x1, 0x1000, my_data)
result = device.mem_read(0x1, 0x1000, 4)

reg_val = device.get_register(dev_id=0, reg_id=5)
print(f"Register Value: {reg_val}")
