#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int* sum_waveform = NULL;  // sum waveform
int sum_waveform_n = 0;  // length of x
int* ourranges = NULL;
int ourrangeindex = 0;
int i = 0, subindex = 0;


int baseline = 0;
void add_samples(int* samples, int n,
		 int t0, int reduction) {
  // This takes an 'occurence', which is data seen by only one PMT
  // and adds it to the sum waveform 'sum_waveform'.
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
    sum_waveform[subindex] += samples[i] - baseline;
  }  
}

void build_events(int **ranges, int *n, int threshold, int gap) {
  // create 2tupes with +/- 180us
  // Then merge with single For loop
  ourrangeindex = 0;
  for (i = 0; i < sum_waveform_n; ++i) {
    if (sum_waveform[i] > threshold) {  // Above threshold
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
  *sum = sum_waveform;
  *n = sum_waveform_n;
}

void shutdown() {
  if (sum_waveform != NULL) free(sum_waveform);
  sum_waveform = NULL;
  if (ourranges != NULL) free(ourranges);
  ourranges = NULL;
}

void setup(int n) {
  if (sum_waveform_n != 0 && sum_waveform_n != n) {
    printf("wax_compiled_helpers already initialized; will try to reinitialize...\n");
    shutdown();
  }
  if (sum_waveform == NULL) {
    sum_waveform = malloc(sizeof(int) * n);
  }
  if (ourranges == NULL) {
    ourranges = malloc(sizeof(int) * n * 2);
  }
  memset(sum_waveform, 0, sizeof(int) * n);
  memset(ourranges, 0, sizeof(int) * n * 2);
  sum_waveform_n = n;
}