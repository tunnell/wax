#include "CaenBlockParsing.h"

unsigned int buffer_size = 0;
short **samples = NULL; // 8xN
unsigned int **indecies = NULL; // 8xN
unsigned int *lengths = NULL; // <N
int nc = 8; // number of channels

int *sum_waveform = NULL; // LONG!
unsigned int length_sum_waveform = 0;

int setup_sum_waveform_buffer(int n){
    
    sum_waveform = (int *) malloc(n*sizeof(int));
    if (sum_waveform == NULL) {
        return 0;
    }
    length_sum_waveform = n;
    return 1;
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


int put_samples_into_occurences(int time_offset, int scale) {
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
    return 0;
}

int get_sum_waveform(int *sum_waveform_out, int n) {
    for(int i=0; i < length_sum_waveform; i++){
        sum_waveform_out[i] = sum_waveform[i];
    }
    return 0;
}

uint32_t swap_uint32( uint32_t val )
{
    val = ((val << 8) & 0xFF00FF00 ) | ((val >> 8) & 0xFF00FF );
    return (val << 16) | (val >> 16);
}

int inplace(unsigned int *buff, int n, int zle_is_off)
{
    unsigned int pnt=0;
    unsigned int CurrentChannel;
    unsigned int size_of_channel_data, cnt, wavecnt;
    unsigned int GoodWords;


    printf("wtf is this %d %d\n", (buff[0] & 0xFFFFFFF), zle_is_off);
    if ((buff[pnt]>>20)==0xA00) {  // check header, where word starts with 0b1010
        pnt++; // Move to second word

        // The second word is the channel mask
        unsigned int ChannelMask = buff[pnt] & 0xFF;  pnt++;
        
        pnt+=2; // Skip event counter and trigger time tag
        
        // For every channel; there are 8 channels
        for (int j = 0; j < 8; j++) {
            lengths[j] = 0;  // Currently, no samples.

            // Read only the channels given in ChannelMask
            if ((ChannelMask>>j)&1) CurrentChannel=j;
            else continue;
            
            if (zle_is_off) {
                printf("ZLE IS OFF\n");
                // No zero suprression!
                size_of_channel_data = ((buff[0] & 0xFFFFFFF) - 4 ) / 8;
                cnt = 0;
            }
            else {  // zeros are suppressed
            printf("ZLE IS On\n");
               size_of_channel_data = buff[pnt];  pnt++;
                cnt=2;   // Don't count control word and 'size' word in counter
             }

            wavecnt=0;           // counter to reconstruct times within waveform
            
            while (cnt <= size_of_channel_data)
            {
                printf("asdf %d <= %d (%d)", cnt, size_of_channel_data, (buff[0] & 0xFFFFFFF));
                if ((buff[pnt]>>28)==0x8 || zle_is_off) { // good data
                    //  This is how many 'good' words there are before, if ZLE, the next
                    // control word.
                    if (zle_is_off) {
                        GoodWords = size_of_channel_data ;  // without ZLE
                    }
                    else {
                        GoodWords = buff[pnt] & 0xFFFFFFF;        pnt++;  cnt++;  // with ZLE
                    }
                    
                    // save waveform in histogram
                    for (int i=0; i<GoodWords; i++) {
                        samples[j][lengths[j]] = buff[pnt] & 0xFFFF;
                        indecies[j][lengths[j]] = wavecnt;
                        printf("sample %hu index %d %d %d \n", samples[j][lengths[j]], indecies[j][lengths[j]], GoodWords, i);
                        lengths[j]++;
                        wavecnt++;
                        
                        samples[j][lengths[j]] = (buff[pnt]>>16) & 0xFFFF;
                        indecies[j][lengths[j]] = wavecnt;
                        printf("sample %hu index %d\n", samples[j][lengths[j]], indecies[j][lengths[j]]);
                        lengths[j]++;
                        wavecnt++;
                        
                        pnt++; cnt++;
                    }
                    
                } else { // skip, can only happen if zle_is_off == false
                    if (buff[pnt]!=0xFFFFFFFF) {
                        wavecnt+=2*buff[pnt]+1;
                        pnt++; cnt++;
                    } else { printf("skip\n"); return -1; }
                }
            } // end while(cnt...)
        } // end for-loop
    } // end Check Header
    else { printf("epic fail Header\n%x\n%x\n",buff[pnt],
    swap_uint32(buff[pnt])); return -2; }
    
    return 1;
}


