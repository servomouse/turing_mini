#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <pthread_time.h>   // Only to make VSCode happy
#include "clock.h"
#include <pthread.h>

#include "lib/utils.h"

#define MAX_NUM_DEVICES 256
#define NSEC_PER_SEC 1000000000L

typedef struct {
    void (*tick_func)(void);
    uint32_t tick_counter;  // Used for the divider functionality
    uint32_t clock_divider;
} device_t;

static uint64_t tick_counter;
static int ticks_per_second;
static int rtm;
static uint64_t target_ns;
static device_t devices[MAX_NUM_DEVICES];

int clock_add_device(void (*tick_func)(void), uint32_t clock_divider) {
    for(int i=0; i<MAX_NUM_DEVICES; i++) {
        if (devices[i].tick_func == NULL) {
            devices[i].tick_func = tick_func;
            devices[i].tick_counter = 0;
            devices[i].clock_divider = clock_divider;
            return i;
        }
    }
    return -1;
}

int init_clock(int freq, int real_time_mode) {
    for(int i=0; i<MAX_NUM_DEVICES; i++) {
        devices[i].tick_func = NULL;
    }
    printf("Init clock, freq: %d, real_time_mode: %s\n", freq, real_time_mode? "True": "False");
    if (real_time_mode == 0) {
        rtm = 0;
    } else {
        rtm = 1;
    }
    ticks_per_second = freq;
    target_ns = NSEC_PER_SEC / ticks_per_second;
    init_xtal_thread();
    return EXIT_SUCCESS;
}

void tick_system() {
    for(int i=0; i<MAX_NUM_DEVICES; i++) {
        if (devices[i].tick_func != NULL) {
            devices[i].tick_counter++;
            if(devices[i].tick_counter == devices[i].clock_divider) {
                devices[i].tick_func();
                devices[i].tick_counter = 0;
            }
        }
    }
}

int run_one_tick(void) {
    struct timespec start, end, delay;
    if (tick_counter > 128) {
        exit(EXIT_SUCCESS);
    }
    if (rtm == 0) {
        tick_system();
    } else {
        clock_gettime(CLOCK_MONOTONIC, &start);
        tick_system();
        clock_gettime(CLOCK_MONOTONIC, &end);
        long elapsed_ns = (end.tv_sec - start.tv_sec) * NSEC_PER_SEC + (end.tv_nsec - start.tv_nsec);

        if (elapsed_ns < target_ns) {
            long remaining_ns = target_ns - elapsed_ns;
            delay.tv_sec = 0;
            delay.tv_nsec = remaining_ns;
            nanosleep(&delay, NULL);
        }
    }
    tick_counter++;
    return EXIT_SUCCESS;
}

typedef enum { STATE_PAUSED, STATE_RUNNING, STATE_STEPPING, STATE_EXIT } system_state_t;

static pthread_t worker_thread;
static pthread_mutex_t state_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t state_cond = PTHREAD_COND_INITIALIZER;
static pthread_cond_t step_done_cond = PTHREAD_COND_INITIALIZER;
static system_state_t current_state = STATE_PAUSED;

static int step_budget = 0;

void* run_xtal(void* arg) {
    printf("run_xtal: Init\n");
    while (1) {
        int just_finished_stepping = 0;
        int keep_running = 0;
        pthread_mutex_lock(&state_mtx);
        switch(current_state) {
            case STATE_EXIT:
                pthread_mutex_unlock(&state_mtx);
                return NULL;
            case STATE_STEPPING:
                printf("run_xtal: STATE_STEPPING\n");
                if (step_budget > 0) {
                    step_budget--;
                    if (step_budget <= 0) { // Will halt on the next iteration
                        current_state = STATE_PAUSED;
                        just_finished_stepping = 1;
                    }
                    keep_running = 1;
                } else {    // Counter was decremented by API, do one more step and halt
                    RAISE("Error: current_state == STATE_STEPPING and step_budget <= 0\n");
                    current_state = STATE_PAUSED;
                }
                break;
            case STATE_RUNNING:
                printf("run_xtal: STATE_RUNNING\n");
                keep_running = 1;
                break;
            case STATE_PAUSED:
                printf("run_xtal: STATE_PAUSED\n");
                pthread_cond_wait(&state_cond, &state_mtx);
                printf("run_xtal: signal received\n");
                break;
            default:
                RAISE("Error: Unknown state: %d\n", current_state);
        }

        pthread_mutex_unlock(&state_mtx);

        if (keep_running) {
            run_one_tick();
        }

        if (just_finished_stepping) {
            pthread_cond_broadcast(&step_done_cond);
        }
    }
}

void xtal_run(void) {
    pthread_mutex_lock(&state_mtx);
    current_state = STATE_RUNNING;
    pthread_cond_signal(&state_cond);
    pthread_mutex_unlock(&state_mtx);
}

void xtal_pause(void) {
    pthread_mutex_lock(&state_mtx);
    current_state = STATE_PAUSED;
    // We don't clear step_budget here, allowing pending steps to finish
    pthread_mutex_unlock(&state_mtx);
}

void xtal_step(uint32_t steps) {
    printf("xtal_step: running %d steps\n", steps);
    pthread_mutex_lock(&state_mtx);
    step_budget += steps;
    current_state = STATE_STEPPING;
    pthread_cond_signal(&state_cond);
    while (step_budget > 0) {
        pthread_cond_wait(&step_done_cond, &state_mtx);
    }
    pthread_mutex_unlock(&state_mtx);
}

void xtal_exit(void) {
    pthread_mutex_lock(&state_mtx);
    current_state = STATE_EXIT;
    pthread_cond_signal(&state_cond);
    pthread_mutex_unlock(&state_mtx);
}

void init_xtal_thread(void) {
    pthread_create(&worker_thread, NULL, run_xtal, NULL);
}
