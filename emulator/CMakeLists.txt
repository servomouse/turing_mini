cmake_minimum_required(VERSION 3.31)

SET(CMAKE_CACHE_DISABLE ON)
# set(CMAKE_C_COMPILER C:\\MinGW\\bin\\gcc.exe)   # 32-bit
set(CMAKE_C_COMPILER C:\\mingw64\\bin\\gcc.exe)   # 64-bit
# set(CMAKE_CXX_COMPILER /c/MinGW/bin/g++)
project(project_name)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)   # Generate compile_commands.json for vscode
include(CTest)
find_package(Python3 REQUIRED)

set(EXECUTABLES_DIR "${CMAKE_BINARY_DIR}/executables")
set(DEVICES_DIR "${CMAKE_SOURCE_DIR}/devices")

add_subdirectory(devices/address_decoder)
add_subdirectory(devices/memory)
add_subdirectory(devices/clock)
add_subdirectory(devices/dummy)
add_subdirectory(tests/test_clock)
# add_subdirectory(lib)
# add_subdirectory(source)
# add_subdirectory(tests)

add_custom_target(
    build-all
    DEPENDS
        clock_lib
        test_clock_dll
)