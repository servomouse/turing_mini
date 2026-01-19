add_test(NAME Test_Python_Integration 
    COMMAND Python3::Interpreter "${CMAKE_CURRENT_SOURCE_DIR}/test_clock.py"
)