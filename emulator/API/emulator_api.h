#pragma once

#include <stdint.h>

#ifdef __unix__
    #define DLL_PREFIX 
#elif defined(_WIN32) || defined(WIN32)
    #define DLL_PREFIX __declspec(dllexport)
#endif

DLL_PREFIX void init(void);
DLL_PREFIX void save_state(char *filename);
DLL_PREFIX void restore_state(char *filename);

DLL_PREFIX void run(void);
DLL_PREFIX void stop(void);
DLL_PREFIX void step(uint32_t num_steps);
DLL_PREFIX void reset(void);

DLL_PREFIX void mem_write(uint32_t memspace, uint32_t offset, uint32_t len, void *data);
DLL_PREFIX void mem_read(uint32_t memspace, uint32_t offset, uint32_t len, void *data);

DLL_PREFIX void set_register(uint32_t dev_id, uint32_t reg_id, uint32_t value);
DLL_PREFIX void get_register(uint32_t dev_id, uint32_t reg_id, uint32_t *value);
