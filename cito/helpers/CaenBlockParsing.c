#include "CaenBlockParsing.h"

// TODO: move to shorts?

unsigned int buffer_size = 0;
short **samples = NULL; // 8xN
unsigned int **indecies = NULL; // 8xN
unsigned int *lengths = NULL; // <N
int nc = 8; // number of channels

short *sum_waveform = NULL; // LONG!
unsigned int length_sum_waveform = 0;

int setup_sum_waveform_buffer(int n){

    sum_waveform = (short *) malloc(n*sizeof(short));
    if (sum_waveform == NULL) {
        return 0;
    }
    length_sum_waveform = n;
    return 1;
}

void cleanup(){
    cleanup_sum_waveform_buffer();
    cleanup_return_buffer();
}

void cleanup_sum_waveform_buffer(){
    free(sum_waveform);
}

void cleanup_return_buffer(){
    if ( samples == NULL || indecies == NULL) {
        return;
    }

    for(int i=0;i<nc;i++){
        free(samples[i]);
        free(indecies[i]);
    }

    free(samples);
    free(indecies);
}


int setup_return_buffer(int n){
  // This leaks memory, so don't call continously!  Call once
  if (samples != NULL || indecies != NULL) {
    return 0;
  }

  samples=(short **) malloc(nc*sizeof(short*));
  indecies=(unsigned int **) malloc(nc*sizeof(unsigned int*));

  lengths = (unsigned int *) malloc(nc*sizeof(unsigned int));

  if (samples == NULL || indecies == NULL) {
    return 0;
  }

  unsigned int size = n* sizeof(unsigned int); // size of channel data
  for(int i=0;i<nc;i++){
    samples[i]=(short*) malloc(size);
    indecies[i] = (unsigned int*) malloc(size);
    memset(samples[i],0,size);
    memset(indecies[i],0,size);
    if (samples[i] == NULL || indecies[i] == NULL) {
      return 0;
    }

    lengths[i] = 0;
    
  }

  return 1;
}

int put_samples_into_occurences(int time_offset, int scale) {
// Cheat.
   unsigned int corrected_time = 0;
   int sample = 0;
  for (int i=0; i < nc; i++) {
    for (int j=0; j < lengths[i]; j++){
        corrected_time = indecies[i][j] + time_offset;
         // check wrap around
         if ( corrected_time >= lengths[i]) {
            continue;
         }
         sample = samples[i][j];
         sample -= 16384;  // 2 ** 14
         sample *= -1;
         sample /= scale;
         sum_waveform[corrected_time] += sample;
    }
  }
}

int get_sum_waveform(short *sum_waveform_out, int n) {
    for(int i=0; i < length_sum_waveform; i++){
        sum_waveform_out[i] = sum_waveform[i];
    }
}

int get_data(short *chan_samples, int n0,
	     unsigned int *chan_indecies, int n1,
	     int channel){
  for (int i=0; i < lengths[channel]; i++){
    chan_samples[i] = samples[channel][i];
    chan_indecies[i] = indecies[channel][i];
  }
  return lengths[channel];
}


int inplace(unsigned int *buff, int n)
{
    int pnt=0; 
    int CurrentChannel;
    int Size, cnt, wavecnt;
    int GoodWords;
  
    // error handling if there is an invalid entry after an event
    if (buff[0]==0xFFFFFFFF) pnt++;

    //printf("%08x\n%08x\n",buff[pnt],buff[pnt+1]);  
    // check header
    if ((buff[pnt]>>20)==0xA00) { //  && (buff[pnt+1]>>20)==0x0) {  // 2nd condition omitted since boardId is stored at this place
      pnt++;
      int ChannelMask=buff[pnt] & 0xFF;          pnt++;

      pnt+=2; 
      
      for (int j=0; j<8; j++) { // read all channels
	lengths[j] = 0;
	// read only the channels given in ChannelMask
	if ((ChannelMask>>j)&1) CurrentChannel=j;
	else continue;
	
	Size=buff[pnt];              // size of next waveform
	//if (CurrentChannel!=channel) { pnt+=Size; continue; }
	//else pnt++;
	//if (j>channel) return 0;      
	pnt++;
	
	cnt=2;                              // counter of waveform data
	wavecnt=0;                          // counter to reconstruct times within waveform
	while (cnt<=Size)
	  {
	    // check for invalids just after good samples
	    if ((buff[pnt]>>28)==0x8) { // good data
	      GoodWords=buff[pnt]&0xFFFFFFF;        pnt++;  cnt++;
              
	      // save waveform in histogram
	      for (int i=0; i<GoodWords; i++) {
		samples[j][lengths[j]] = buff[pnt] & 0xFFFF;
		indecies[j][lengths[j]] = wavecnt;
		lengths[j]++;
		wavecnt++;

		samples[j][lengths[j]] = (buff[pnt]>>16) & 0xFFFF;
		indecies[j][lengths[j]] = wavecnt;
		lengths[j]++;
		wavecnt++;
		
		pnt++; cnt++;
	      }
	      
	    } else { // skip
	      if (buff[pnt]!=0xFFFFFFFF) {
		wavecnt+=2*buff[pnt]+1;
		pnt++; cnt++;
	      } else { printf("skip\n"); return -1; }
	    }
	  } // end while(cnt...)
      } // end for-loop
    } // end Check Header 
    else { printf("Header\n%x\n%x",buff[pnt],buff[pnt+1]); return -2; }

    return 1;
}


