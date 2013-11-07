#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h> // memset

void cleanup_sum_waveform_buffer();
void cleanup_return_buffer();
void cleanup();
int setup_sum_waveform_buffer(int n);
int get_sum_waveform(int *sum_waveform_out, int n);

int setup_return_buffer(int n);

int inplace(unsigned int *invec, int n, int zle_is_off);


int put_samples_into_occurences(int time_offset, int scale);