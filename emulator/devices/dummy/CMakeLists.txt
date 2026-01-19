
add_library(dummy_device_lib STATIC 
    math_utils.cpp 
    data_processor.cpp
)

target_include_directories(dummy_device_lib PRIVATE 
    ${PROJECT_SOURCE_DIR}
)