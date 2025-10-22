A simple 4-bit CPU which is basically a Turing machine with an instruction set inspired by the BrainFuck language. The instruction set was expanded to make it more useful.

Instruction set encoding and description:

| Encoding              | Mnemonics | Description |
|-----------------------|-----------|-------------|
|0b0000_xxx0            | SLEEP     | Wait for an interrupt|
|0b0000_xxx1            | ZERO      | Zero out the current cell |
|0b0001_xxxx            | RET       | Return from interrupt |
|0b0010 + 4-bit address | IN        | Load a value from the IO port into the current cell |
|0x0011 + 4-bit address | OUT       | Print the content of the current cell to an IO port |
|0b0100 + 4-bit value   | INC       | Increment the current cell |
|0b0101 + 4-bit value   | DEC       | Decrement the current cell |
|0b0110 + 4-bit value   | PINC      | Increment the pointer to the cell (move the head forward) |
|0b0111 + 4-bit value   | PDEC      | Decrement the pointer to the cell (move the head backwards) |
|0b10 + 6-bit offset    | JZ        | Relative jump if current cell == 0 |
|0b11 + 6-bit offset    | JNZ       | relative jump if current cell != 0 |

Expected program memory layout:

| Offset | Content                            |
|--------|------------------------------------|
|0x00 | (int 0) main function pointer         |
|0x01 | (int 1) interrupt 1 handler pointer   |
|0x02 | (int 2) interrupt 2 handler pointer   |
| ... | ...                                   |
|0x0F | (int 15) interrupt 15 handler pointer |
|0x10...0xFF | Executable code                |

IO ports map:
| Addr | Function       |
|------|----------------|
|0x00  | UART MSB nibble|
|0x01  | UART LSB nibble|
|0x02  | N/A            |
|0x03  | N/A            |
|0x04  | N/A            |
|0x05  | N/A            |
|0x06  | N/A            |
|0x07  | N/A            |
|0x08  | N/A            |
|0x09  | N/A            |
|0x0A  | N/A            |
|0x0B  | N/A            |
|0x0C  | N/A            |
|0x0D  | N/A            |
|0x0E  | N/A            |
|0x0F  | N/A            |
