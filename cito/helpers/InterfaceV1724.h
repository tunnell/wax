#include <stdlib.h>
#include <stdio.h>

int setup_return_buffer(int n);
int get_data(unsigned int *chan_samples,
	     int n0,
	     unsigned int *chan_indecies,
	     int n1,
	     int channel);
int inplace(unsigned int *invec, int n);

