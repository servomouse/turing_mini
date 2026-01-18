#pragma once

#include <stdint.h>

typedef struct {
    void (*tick)(void);
} clock_iface_t;