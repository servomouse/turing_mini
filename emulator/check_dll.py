import pefile

dll_path = "bin/executables/libtest_clock_dll.dll"
pe = pefile.PE(dll_path)

if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
    print(f"--- Dependencies for {dll_path} ---")
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        # This prints the name of the external DLL (e.g., KERNEL32.dll)
        print(entry.dll.decode('utf-8'))
else:
    print("This DLL appears to have no external dependencies (Self-contained).")