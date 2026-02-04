#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "dummy.h"

#define TEST_BUF_SIZE 128
static uint8_t test_buf[TEST_BUF_SIZE];
static uint32_t tick_counter;

static void init(void) {
    return;
}

static void tick(void) {
    tick_counter++;
    printf("Dummy device tick counter: %d\n", tick_counter);
}

static uint32_t get_buf_size(void) {
    return TEST_BUF_SIZE;
}

static void save_state(uint8_t *buf) {
    // uint8_t *buf = (uint8_t*)calloc(TEST_BUF_SIZE, sizeof(uint8_t));
    memmove(buf, test_buf, sizeof(test_buf));
    buf[12] = 23;
    buf[28] = 98;
}

static void restore_state(uint8_t *buf) {
    memmove(test_buf, buf, sizeof(test_buf));
    if ((test_buf[12] != 23) || (test_buf[28] != 98)) {
        printf("Error: Device state restore failed!\n");
    }
}

static void set_register(uint32_t reg_id, uint32_t value) {
    test_buf[reg_id] = value;
}

static void get_register(uint32_t reg_id, uint32_t *value) {
    *value = test_buf[reg_id];
}

static void reset(void) {
    return;
}

void dummy_device_get_device_iface(device_iface_t *iface) {
    iface->init = init;
    iface->tick = tick;
    iface->get_buf_size = get_buf_size;
    iface->save_state = save_state;
    iface->restore_state =restore_state;
    iface->get_register = get_register;
    iface->set_register = set_register;
    iface->reset = reset;
}
