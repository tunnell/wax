#include <stdlib.h>
#include <stdio.h>
#include <string.h> // memset

void cleanup_sum_waveform_buffer();
void cleanup_return_buffer();
void cleanup();
int setup_sum_waveform_buffer(int n);
int get_sum_waveform(short *sum_waveform_out, int n);

int setup_return_buffer(int n);
int get_data(short *chan_samples,
	     int n0,
	     unsigned int *chan_indecies,
	     int n1,
	     int channel);
int inplace(unsigned int *invec, int n);


int put_samples_into_occurences(int time_offset, int scale);