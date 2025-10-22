A simple 4-bit CPU which is basically a Turing machine with an instruction set inspired by the BrainFuck language. The instruction set was expanded to make it more useful.
Instruction set description:
- JZ - relative jump if currect cell == 0
- JNZ - relative jump if currect cell != 0
- INC - Increment the current cell
- DEC - Decrement the current cell
- PINC - Increment the pointer to the cell (move the head forward)
- PDEC - Decrement the pointer to the cell (move the head backwards)
- OUT - Print the content of the current cell to an IO port
- IN - Load a value from the IO port into the current cell
- RET - Return from interrupt
- SLEEP - Wait for an interrupt