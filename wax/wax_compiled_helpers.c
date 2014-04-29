#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int* x = NULL;
int xn = 0;
int* ourranges = NULL;
int ourrangeindex = 0;
int i = 0, subindex = 0;



int baseline = 0;
void add_samples(int* samples, int n,
		 int t0, int reduction) {
  
  for (i = 0; i < n; ++i) {
    samples[i] = -1 * samples[i] + 16384;
  }

  baseline = 0;
  baseline += samples[0];
  baseline += samples[1];
  baseline += samples[2];
  baseline /= 3;
  for (i = 0; i < n; ++i) {
    subindex = (t0 + i) / reduction;
    x[subindex] += samples[i] - baseline;
  }  
}

//18000

void build_events(int **ranges, int *n, int threshold, int gap) {
  // create 2tupes with +/- 180us
  // Then merge with single For loop
  ourrangeindex = 0;
  for (i = 0; i < xn; ++i) {
    if (x[i] > threshold) {  // Above threshold 
      int start = i - gap;
      int stop = i + gap;
      if ( ourrangeindex > 0 && start < ourranges[ourrangeindex - 1]) {
	    ourranges[ourrangeindex - 1] = stop;
      }
      else {
        ourranges[ourrangeindex] = start;
        ourranges[ourrangeindex + 1] = stop;
        ourrangeindex += 2;
      }
    }
  }
  *ranges = ourranges;
  *n = ourrangeindex;
}

void overlaps(int **samples_indices, int *n,
	      int *samples_ranges, int n2) {
  // output - samples_indices		      
  //   ->  output[i] = where samples[i] located
  // input - samples_ranges (len 2n=n2)
  int* data = malloc(n2/2 * sizeof(int));

  int current_range_i = 0;

  for (i = 0; i < n2; i += 2) {
    int sample_start = samples_ranges[i];
    int sample_stop = samples_ranges[i + 1]; 
    
    if (ourranges[2 * current_range_i + 1] < sample_start) {
      // Sample is starting after our event ends, thus move to next event
      current_range_i += 1;

      if (2 * current_range_i >= ourrangeindex ){
	data[i/2] = -1; // -1 means sample has no event     
	continue;
      }

    }

    if (sample_stop < ourranges[2 * current_range_i]) { 
      // skip event
      data[i/2] = -1; // -1 means sample has no event
    } else {
      // Save
      data[i/2] = current_range_i;
    }
  }

  *samples_indices = data;
  *n = n2/2;
}

void get_sum(int** sum, int *n) {
  *sum = x;
  *n = xn;
}

void shutdown() {
  if (x != NULL) free(x);
  x = NULL;
  if (ourranges != NULL) free(ourranges);
  ourranges = NULL;
}

void setup(int n) {
  if (xn != 0 && xn != n) {
    printf("wax_compiled_helpers already initialized; will try to reinitialize...\n");
    shutdown();
  }
  if (x == NULL) {
    x = malloc(sizeof(int) * n);
  }
  if (ourranges == NULL) {
    ourranges = malloc(sizeof(int) * n * 2);
  }
  memset(x, 0, sizeof(int) * n);
  memset(ourranges, 0, sizeof(int) * n * 2);
  xn = n;
}