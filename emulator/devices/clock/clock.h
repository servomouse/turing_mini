#pragma once

#include <stdint.h>

#define RAISE(msg, ...) printf(msg " (line %d in file %s)\n", ##__VA_ARGS__, __LINE__, __FILE__); fflush(stdout); exit(EXIT_FAILURE)

/**
 * @brief Connect device to xtal
 *
 * @param[void (*tick)(void)] tick The tick function of the device
 * @param[int] clock_divider The device will be called each clock_divider clock of xtal
 * @return Device id [0...] or EXIT_FAILURE in case of error
 */
int clock_add_device(void (*tick)(void), uint32_t clock_divider);

/**
 * @brief Initialises clock
 * @details If real_time_mode set and xtal can run faster than real time, it will add sleep periods to each cycle to run at real time
 *
 * @param[int] freq Ticks per second
 * @param[int] real_time_mode 0: run as fast as possible; 1: do not run faster than real time
 * @return Device id [0...] or EXIT_FAILURE in case of error
 */
int init_clock(int freq, int real_time_mode);

// --- Control Functions ---

void xtal_run(void);
void xtal_pause(void);
void xtal_step(uint32_t steps);
void xtal_exit(void);
void init_xtal_thread(void);
