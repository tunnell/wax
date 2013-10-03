#include <stdlib.h>
#include <stdio.h>
#include <string.h> // memset

int setup_return_buffer(int n);
int get_data(int *chan_samples,
	     int n0,
	     unsigned int *chan_indecies,
	     int n1,
	     int channel);
int inplace(unsigned int *invec, int n);


int put_samples_into_occurences(int *chan_samples, int n0, int time_offset, int scale);