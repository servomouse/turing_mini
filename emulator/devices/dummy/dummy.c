#include <stdlib.h>
#include "dummy.h"

#define TEST_BUF_SIZE 128
uint8_t test_buf[TEST_BUF_SIZE];
uint32_t tick_counter;

void init(void) {
    return;
}

void tick(void) {
    tick_counter++;
    printf("Hello world!!!\n");
}

void *save_state(uint32_t *buf_size) {
    uint8_t *buf = (uint8_t*)calloc(TEST_BUF_SIZE, sizeof(uint8_t));
    for(int i=0; i<TEST_BUF_SIZE; i++) {
        buf[i] = test_buf[i];
    }
    buf[12] = 23;
    buf[28] = 98;
    *buf_size = TEST_BUF_SIZE;
    return buf;
}

int restore_state(void *buf) {
    for(int i=0; i<TEST_BUF_SIZE; i++) {
        test_buf[i] = ((uint8_t*)buf)[i];
    }
    if ((test_buf[12] != 23) || (test_buf[28] != 98)) {
        printf("Error: Device state restore failed!\n");
    }
}

void set_register(uint32_t reg_id, uint32_t value) {
    test_buf[reg_id] = value;
}
void get_register(uint32_t reg_id, uint32_t *value) {
    *value = test_buf[reg_id];
}
