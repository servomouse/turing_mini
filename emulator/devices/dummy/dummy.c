#include <stdlib.h>
#include <string.h>
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

uint8_t *save_state(uint32_t *buf_size) {
    uint8_t *buf = (uint8_t*)calloc(TEST_BUF_SIZE, sizeof(uint8_t));
    memmove(buf, test_buf, sizeof(test_buf));
    buf[12] = 23;
    buf[28] = 98;
    *buf_size = TEST_BUF_SIZE;
    return buf;
}

int restore_state(uint8_t *buf) {
    memmove(test_buf, buf, sizeof(test_buf));
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

device_iface_t get_device_iface(void) {
    device_iface_t iface = {
        .init = init,
        .tick = tick,
        .save_state = save_state,
        .restore_state =restore_state,
        .get_register = get_register,
        .set_register = set_register
    };
    return iface;
}
