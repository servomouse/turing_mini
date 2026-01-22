#pragma once

#include <stdint.h>

/* Each device should inplement the following functions:
    void init(void);
    void tick(void);
    uint8_t *save_state(uint32_t *buf_size);   // Buf size: siz in bytes
    int restore_state(uint8_t *buf);
    void set_register(uint32_t reg_id, uint32_t value);
    void get_register(uint32_t reg_id, uint32_t *value);
*/

typedef struct {
    void (*init)(void);
    void (*tick)(void);
    uint32_t (*get_buf_size)(void);
    void (*save_state)(uint8_t*);
    void (*restore_state)(uint8_t*);
    void (*set_register)(uint32_t, uint32_t);
    void (*get_register)(uint32_t, uint32_t*);
    void (*reset)(void);
} device_iface_t;

device_iface_t get_device_iface(void);
