#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <pthread_time.h>   // Only to make VSCode happy
#include "clock.h"
#include <pthread.h>

#define MAX_NUM_DEVICES 256
#define NSEC_PER_SEC 1000000000L

typedef struct {
    void (*tick_func)(void);
    uint32_t tick_counter;
} device_t;

int ticks_per_second;
int real_time_mode;
uint64_t target_ns;

device_t devices[MAX_NUM_DEVICES];

int add_device(void (*tick_func)(void), int clock_divider) {
    return -1;
}

int init_clock(int freq, int real_time_mode) {
    for(int i=0; i<MAX_NUM_DEVICES; i++) {
        devices[i].tick_func = NULL;
    }
    if (real_time_mode == 0) {
        real_time_mode = 0;
    } else {
        real_time_mode = 1;
    }
    ticks_per_second = freq;
    target_ns = NSEC_PER_SEC / ticks_per_second;
    init_xtal_thread();
    return EXIT_SUCCESS;
}

void perform_work() {   // TODO: DeleteMe
    printf("Hello world!!!\n");
}

int run_one_tick(void) {
    struct timespec start, end, delay;
    if (real_time_mode == 0) {
        perform_work();
    } else {
        clock_gettime(CLOCK_MONOTONIC, &start);
        perform_work();
        clock_gettime(CLOCK_MONOTONIC, &end);
        long elapsed_ns = (end.tv_sec - start.tv_sec) * NSEC_PER_SEC + (end.tv_nsec - start.tv_nsec);

        if (elapsed_ns < target_ns) {
            long remaining_ns = target_ns - elapsed_ns;
            delay.tv_sec = 0;
            delay.tv_nsec = remaining_ns;
            nanosleep(&delay, NULL);
        }
    }
    return EXIT_SUCCESS;
}

typedef enum { STATE_PAUSED, STATE_RUNNING, STATE_STEPPING, STATE_EXIT } system_state_t;

static pthread_t worker_thread;
static pthread_mutex_t state_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t state_cond = PTHREAD_COND_INITIALIZER;
static system_state_t current_state = STATE_PAUSED;

static int step_budget = 0;

void* run_xtal(void* arg) {
    while (1) {
        pthread_mutex_lock(&state_mtx);
        switch(current_state) {
            case STATE_EXIT:
                pthread_mutex_unlock(&state_mtx);
                return NULL;
            case STATE_STEPPING:
                if (step_budget > 0) {
                    step_budget--;
                    if (step_budget <= 0) {
                        current_state = STATE_PAUSED;
                    }
                } else {    // Counter was decremented by API, do one more step and halt
                    printf("Error: current_state == STATE_STEPPING and step_budget <= 0\n");
                    current_state = STATE_PAUSED;
                }
                break;
            case STATE_PAUSED:
                pthread_cond_wait(&state_cond, &state_mtx);
                break;
            default:
                printf("Error: Unknown state: %d\n", current_state);
        }

        pthread_mutex_unlock(&state_mtx);

        run_one_tick(); 
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
    pthread_mutex_lock(&state_mtx);
    step_budget += steps;
    current_state = STATE_STEPPING;
    pthread_cond_signal(&state_cond);
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
