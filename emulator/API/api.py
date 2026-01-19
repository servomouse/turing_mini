import ctypes
from ctypes import POINTER, c_uint32, c_char_p, c_void_p

class CPUEmulatorAPI:
    def __init__(self, lib_path="./emulator.dll"):
        # Load the DLL
        try:
            self.lib = ctypes.CDLL(lib_path)
        except OSError as e:
            print(f"Error: Could not find or load the DLL at {lib_path}")
            raise e

        self._setup_prototypes()
        # Initialize the emulator core
        self.lib.init()

    def _setup_prototypes(self):
        """Define argument and return types for the DLL functions."""
        
        # State Management
        self.lib.save_state.argtypes = [c_char_p]
        self.lib.restore_state.argtypes = [c_char_p]

        # Execution Control
        self.lib.run.argtypes = []
        self.lib.stop.argtypes = []
        self.lib.step.argtypes = [c_uint32]
        self.lib.reset.argtypes = []

        # Memory Access
        # void mem_write(uint32_t memspace, uint32_t offset, uint32_t len, void *data)
        self.lib.mem_write.argtypes = [c_uint32, c_uint32, c_uint32, c_void_p]
        self.lib.mem_read.argtypes = [c_uint32, c_uint32, c_uint32, c_void_p]

        # Register Access
        self.lib.set_register.argtypes = [c_uint32, c_uint32, c_uint32]
        # Note: Your C signature for get_register likely needs a pointer to return a value
        self.lib.get_register.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]

    # --- Wrapper Methods ---

    def save(self, filename: str):
        self.lib.save_state(filename.encode('utf-8'))

    def load(self, filename: str):
        self.lib.restore_state(filename.encode('utf-8'))

    def run(self):
        self.lib.run()

    def stop(self):
        self.lib.stop()

    def step(self, count=1):
        self.lib.step(c_uint32(count))

    def reset(self):
        self.lib.reset()

    def write_memory(self, memspace, offset, data_bytes):
        """Writes a bytes object or bytearray to the emulator memory."""
        length = len(data_bytes)
        # Create a temporary buffer ctypes can understand
        buffer = (ctypes.c_ubyte * length).from_buffer_copy(data_bytes)
        self.lib.mem_write(memspace, offset, length, buffer)

    def read_memory(self, memspace, offset, length):
        """Reads 'length' bytes from the emulator and returns a python bytes object."""
        buffer = (ctypes.c_ubyte * length)()
        self.lib.mem_read(memspace, offset, length, buffer)
        return bytes(buffer)

    def set_reg(self, dev_id, reg_id, value):
        self.lib.set_register(dev_id, reg_id, value)

    def get_reg(self, dev_id, reg_id):
        val = c_uint32()
        self.lib.get_register(dev_id, reg_id, ctypes.byref(val))
        return val.value