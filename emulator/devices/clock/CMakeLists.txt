set(EXECUTABLES_DIR "${CMAKE_BINARY_DIR}/executables")

add_executable(clock
    clock.c
)

add_custom_command(TARGET clock POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory ${EXECUTABLES_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:clock> ${EXECUTABLES_DIR}
    COMMENT "Copying binary to root bin folder..."
)