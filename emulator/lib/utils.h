#pragma once

#define RAISE(msg, ...) printf(msg " (line %d in file %s)\n", ##__VA_ARGS__, __LINE__, __FILE__); fflush(stdout); exit(EXIT_FAILURE)
