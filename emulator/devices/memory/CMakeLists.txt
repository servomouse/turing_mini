
add_library(memory_device_lib STATIC
    memory.c
)

target_include_directories(memory_device_lib PRIVATE
    ${CMAKE_SOURCE_DIR}
)
