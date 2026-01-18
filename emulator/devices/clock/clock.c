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
    clock_iface_t *iface;
    uint32_t tick_counter;
} device_t;

int ticks_per_second;
int real_time_mode;

device_t devices[MAX_NUM_DEVICES];

int add_device(clock_iface_t dev, int clock_divider) {
    return -1;
}

int init_clock(int freq, int real_time_mode) {
    for(int i=0; i<MAX_NUM_DEVICES; i++) {
        devices[i].iface = NULL;
    }
    if (real_time_mode == 0) {
        real_time_mode = 0;
    } else {
        real_time_mode = 1;
    }
    ticks_per_second = freq;
    return EXIT_SUCCESS;
}

void perform_work() {   // TODO: DeleteMe
    printf("Hello world!!!\n");
}

int run_system(void) {
    // The total time budget for one single tick in nanoseconds
    long target_ns = NSEC_PER_SEC / ticks_per_second;
    struct timespec start, end, delay;
    if (real_time_mode == 0) {
        perform_work();
    } else {
        while (1) {
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
    }
    return EXIT_SUCCESS;
}

typedef enum { STATE_PAUSED, STATE_RUNNING, STATE_STEPPING, STATE_EXIT } system_state_t;

static pthread_t worker_thread;
static pthread_mutex_t state_mtx = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t state_cond = PTHREAD_COND_INITIALIZER;
static system_state_t current_state = STATE_PAUSED;

static int step_budget = 0; // Number of steps queued
static int is_running = 0;  // 1 if in Run mode, 0 if Paused, -1 is a signal to exit

void* run_xtal(void* arg) {
    while (1) {
        pthread_mutex_lock(&state_mtx);
        
        // Wait while we have no budget AND we aren't in 'Run' mode
        while (step_budget <= 0 && !is_running) {
            if (current_state == STATE_EXIT) { 
                pthread_mutex_unlock(&state_mtx);
                return NULL;
            }
            pthread_cond_wait(&state_cond, &state_mtx);
        }

        // If we were stepping, consume one unit of the budget
        if (!is_running && step_budget > 0) {
            step_budget--;
        }

        pthread_mutex_unlock(&state_mtx);

        // --- Execute Work ---
        execute_timed_work(); 
    }
}

// --- Control Functions ---

void xtal_run() {
    pthread_mutex_lock(&state_mtx);
    is_running = 1;
    current_state = STATE_RUNNING;
    pthread_cond_signal(&state_cond);
    pthread_mutex_unlock(&state_mtx);
}

void xtal_pause() {
    pthread_mutex_lock(&state_mtx);
    current_state = STATE_PAUSED;
    is_running = 0;
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

void xtal_exit() {
    pthread_mutex_lock(&state_mtx);
    is_running = -1;
    current_state = STATE_EXIT;
    pthread_cond_signal(&state_cond);
    pthread_mutex_unlock(&state_mtx);
}

void init_xtal_thread() {
    pthread_create(&worker_thread, NULL, run_xtal, NULL);
}
