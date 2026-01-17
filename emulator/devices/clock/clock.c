#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <pthread_time.h>   // Only to make VSCode happy
#include "clock.h"

#define MAX_NUM_DEVICES 256
#define TICKS_PER_SECOND 10
#define NSEC_PER_SEC 1000000000L

typedef struct {
    clock_iface_t *iface;
    uint32_t tick_counter;
} device_t;

device_t devices[MAX_NUM_DEVICES];

int reset_clock(void) {
    for(int i=0; i<MAX_NUM_DEVICES; i++) {
        devices[i].iface = NULL;
    }
    return EXIT_SUCCESS;
}

void perform_work() {   // TODO: DeleteMe
    printf("Hello world!!!\n");
}


int add_device(clock_iface_t dev, int clock_divider) {
    return -1;
}

int main() {
    // The total time budget for one single tick in nanoseconds
    long target_ns = NSEC_PER_SEC / TICKS_PER_SECOND;
    
    struct timespec start, end, delay;

    while (1) {
        // 1. Record the start time of the cycle
        clock_gettime(CLOCK_MONOTONIC, &start);

        // 2. Perform the task
        perform_work();

        // 3. Record the end time
        clock_gettime(CLOCK_MONOTONIC, &end);

        // 4. Calculate how long the work took (in nanoseconds)
        long elapsed_ns = (end.tv_sec - start.tv_sec) * NSEC_PER_SEC + 
                          (end.tv_nsec - start.tv_nsec);

        // 5. If we have time left, sleep for the remainder
        if (elapsed_ns < target_ns) {
            long remaining_ns = target_ns - elapsed_ns;
            
            delay.tv_sec = 0;
            delay.tv_nsec = remaining_ns;
            
            nanosleep(&delay, NULL);
        } 
        // Else: Work took longer than target_ns, so we skip sleep
    }
    return EXIT_SUCCESS;
}
