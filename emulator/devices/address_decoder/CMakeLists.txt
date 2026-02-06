
add_library(address_decoder_device_lib STATIC
    address_decoder.c
)

target_include_directories(address_decoder_device_lib PRIVATE
    ${CMAKE_SOURCE_DIR}
)
