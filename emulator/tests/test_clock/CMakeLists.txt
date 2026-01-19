# add_executable(test-clock
#     main.c
# )
add_library(test_clock_dll SHARED test_clock.c)

target_include_directories(test-clock PRIVATE
    ${DEVICES_DIR}
)

add_custom_command(TARGET test-clock POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory ${EXECUTABLES_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:test-clock> ${EXECUTABLES_DIR}
    COMMENT "Copying binary to root bin folder..."
)