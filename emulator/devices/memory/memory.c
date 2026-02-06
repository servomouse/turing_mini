#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <stdarg.h>
#include <string.h>

#include "memory.h"
#include "lib/utils.h"

#define LOG_FILE            "memory.log"
#define DEVICE_DATA_FILE    "data/memory.bin"

typedef struct {
    uint32_t MEM_SIZE;
} device_regs_t;

device_regs_t regs;
DATA_BUS_WIDTH *memory;

DATA_BUS_WIDTH memory_read(uint32_t address) {
    if(address < regs.MEM_SIZE) {
        DATA_BUS_WIDTH val = memory[address];
        return val;
    } else {
        RAISE("Error: Attempting to read from outside of memory! Addr: %d\n", address);
    }
}

void memory_write(ADDR_BUS_WIDTH address, DATA_BUS_WIDTH val) {
    if(address < regs.MEM_SIZE) {
        memory[address] = val;
    } else {
        RAISE("Error: Attempting to write outside of memory! Addr: %d\n", address);
    }
}

void memory_write_array(ADDR_BUS_WIDTH offset, uint32_t size, const DATA_BUS_WIDTH *data) {
    if((offset+size) > regs.MEM_SIZE) {
        RAISE("Error: Attempting to write data outside of the memory!\n");
    }
    for(uint32_t i=0; i<size; i++) {
        memory[offset+i] = data[i];
    }
}

void module_init(uint32_t mem_size) {
    regs.MEM_SIZE = mem_size;
    if(memory != NULL) free(memory);
    fflush(stdout);
    memory = (DATA_BUS_WIDTH*)calloc(regs.MEM_SIZE, sizeof(DATA_BUS_WIDTH));
}

void module_reset(void) {
    memset(&regs, 0, sizeof(device_regs_t));
}
