#pragma once

#include "clock_header.h"


/**
 * @brief Connect device to xtal
 *
 * @param[clock_iface_t] dev The clock interface of the device
 * @param[int] clock_divider The device will be called each clock_divider clock of xtal
 * @return Device id [0...] or EXIT_FAILURE in case of error
 */
int add_device(clock_iface_t dev, int clock_divider);

