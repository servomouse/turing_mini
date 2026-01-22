# add_executable(clock
#     clock.c
# )

add_library(clock_lib STATIC 
    clock.c
)

# add_custom_command(TARGET clock_lib POST_BUILD
#     COMMAND ${CMAKE_COMMAND} -E make_directory ${EXECUTABLES_DIR}
#     COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:clock_lib> ${EXECUTABLES_DIR}
#     COMMENT "Copying binary to root bin folder..."
# )