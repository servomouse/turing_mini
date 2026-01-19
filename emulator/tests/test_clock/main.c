#include <stdlib.h>
#include <stdio.h>
#include "clock/clock.h"
#include "API/emulator_api.h"

void init(void);
void save_state(char *filename);
void restore_state(char *filename);

void run(void);
void stop(void);
void step(uint32_t num_steps);
void reset(void);

void mem_write(uint32_t memspace, uint32_t offset, uint32_t len, void *data);
void mem_read(uint32_t memspace, uint32_t offset, uint32_t len, void *data);

void set_register(uint32_t dev_id, uint32_t reg_id, uint32_t value);
void get_register(uint32_t dev_id, uint32_t reg_id, uint32_t *value);
