
add_library(dummy_device_lib STATIC 
    dummy.c
)

target_include_directories(dummy_device_lib PRIVATE 
    ${CMAKE_SOURCE_DIR}
)