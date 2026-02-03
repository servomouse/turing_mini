# add_executable(test-clock
#     main.c
# )
add_library(test_clock_dll SHARED main.c)

target_include_directories(test_clock_dll PUBLIC
    ${DEVICES_DIR}
    ${CMAKE_SOURCE_DIR}
)

target_link_libraries(test_clock_dll
    # Force static linking
    $<TARGET_FILE:dummy_device_lib> 
    $<TARGET_FILE:clock_lib>
)

if(WIN32)
    # Target the specific DLL
    target_link_options(test_clock_dll PRIVATE
        "-static"
        "-static-libgcc"
        "-static-libstdc++"
    )
endif()

add_custom_command(TARGET test_clock_dll POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory ${EXECUTABLES_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:test_clock_dll> ${EXECUTABLES_DIR}
    COMMENT "Copying binary to root bin folder..."
)