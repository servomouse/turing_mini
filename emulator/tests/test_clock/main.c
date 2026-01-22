#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "clock/clock.h"
#include "API/emulator_api.h"
#include "API/device_api.h"

// Devices:
#include "dummy/dummy.h"

#define MAX_DEV_NUM 128

device_iface_t *devices[MAX_DEV_NUM];
uint32_t num_devices;

typedef struct {
    uint32_t size;
    uint8_t data[0];
} device_state_t;

void init(void) {
    devices[0] = calloc(1, sizeof(device_iface_t));
    dummy_device_get_device_iface(devices[0]);
    num_devices++;
}

void save_state(char *filename) {
    uint32_t buf_size = sizeof(num_devices);
    uint8_t *buf = malloc(buf_size);
    memmove(buf, &num_devices, sizeof(num_devices));
    for(int i=0; i<num_devices; i++) {
        uint32_t buf_size_inc = sizeof(device_state_t) + devices[0]->get_buf_size(&buf_size);
        realloc(buf, buf_size+buf_size_inc);
        device_state_t *dev_state = (device_state_t *)&buf[buf_size+1];
        devices[i]->save_state(dev_state->data);
        buf_size += buf_size_inc;
    }

    FILE *fptr;
    if ((fptr = fopen(filename, "wb")) == NULL) {
        printf("Error! opening file");
        exit(1);
    }
    fwrite(buf, 1, buf_size, fptr);
    fclose(fptr);
    free(buf);
}

void restore_state(char *filename) {
    FILE *file_ptr;
    unsigned char *buffer;
    long file_len;

    file_ptr = fopen(filename, "rb");
    if (file_ptr == NULL) {
        perror("Error opening file");
        return 1;
    }

    fseek(file_ptr, 0, SEEK_END);
    file_len = ftell(file_ptr);
    fseek(file_ptr, 0, SEEK_SET);

    buffer = (unsigned char *)calloc(file_len + 1, 1);
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file_ptr);
        return 1;
    }

    size_t bytes_read = fread(buffer, 1, file_len, file_ptr);
    if (bytes_read != file_len) {
        fprintf(stderr, "Error reading file, read %zu bytes out of %ld\n", bytes_read, file_len);
        free(buffer);
        fclose(file_ptr);
        return 1;
    }

    printf("Read %ld bytes from file. Contents:\n", file_len);

    num_devices = ((uint32_t*)buffer)[0];
    uint32_t offset = sizeof(uint32_t);
    for (int i = 0; i < num_devices; i++) {
        device_state_t *buf = (device_state_t*)&buffer[offset];
        offset += buf->size;
        devices[i]->restore_state(buf->data);
    }
    free(buffer);
    fclose(file_ptr);
}

void run(void);
void stop(void);
void step(uint32_t num_steps);
void reset(void);

void mem_write(uint32_t memspace, uint32_t offset, uint32_t len, void *data);
void mem_read(uint32_t memspace, uint32_t offset, uint32_t len, void *data);

void set_register(uint32_t dev_id, uint32_t reg_id, uint32_t value);
void get_register(uint32_t dev_id, uint32_t reg_id, uint32_t *value);
