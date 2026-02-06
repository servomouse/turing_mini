#pragma once

#include <stdint.h>

#define ADDR_BUS_WIDTH uint16_t
#define DATA_BUS_WIDTH uint8_t

typedef DATA_BUS_WIDTH(mem_read_func_t) (ADDR_BUS_WIDTH);            // param: address, ret_val: read value
typedef void   (mem_write_func_t)(ADDR_BUS_WIDTH, DATA_BUS_WIDTH);   // params: address, value to write
