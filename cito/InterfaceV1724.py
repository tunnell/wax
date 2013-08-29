"""Interface to Caen V1724

Flash ADC board
"""

import pymongo
import numpy as np

SAMPLE_TYPE = np.uint16 # Samples are actually 14 bit
MAX_ADC_VALUE = 2 ** 14   # 14 bit ADC samples
SAMPLE_TIME_STEP = 1    # 10 ns
WORD_SIZE_IN_BYTES = 4  # 4 bytes in a 32 bit word


def get_word(data):
    """Generator for words
    """
    word_size_in_bytes = 4

    number_of_words = int(len(data) / word_size_in_bytes)
    for i in range(number_of_words):
        yield get_word_by_index(data, i)


def get_word_by_index(data, i, do_checks=True):
    """Get 32-bit word by index

    This function is called often so be sure to check
    """
    if do_checks:
        if len(data) == 0:
            print("Warning: data has zero length")
        if i > int(len(data) / 4):
            raise IndexError('i does not exist')

    i0 = i*WORD_SIZE_IN_BYTES
    i1 = (i+1)*WORD_SIZE_IN_BYTES

    word = int.from_bytes(data[i0:i1], 'little')

    return word

def check_header(data):
    word = get_word_by_index(data, 0)
    assert(word >> 20 == 0xA00)

def get_event_size(data):
    check_header(data)
    word = get_word_by_index(data, 0)
    size = (word & 0x0FFFFFFF)
    assert(size == int(len(data)/4))
    return size # number of words

def get_trigger_time_tag(data):
    check_header(data)
    word = get_word_by_index(data, 3)

    # The trigger time is a 31 bit number.  The 32nd bit is pointless since it
    # is zero for the first clock cycle then 1 for each cycle afterward.  This
    # information from from Dan Coderre (Bern).  28/Aug/2013.
    word = word & 0x7FFFFFFF

    return word

def get_waveform(data, module, offset=0):
    # TODO: maybe make an 8 by N_SAMPLES array?  Makes easier to use numpy routines.

    # Each 'occurence' is a continous sequence of ADC samples for a given
    # channel.  Due to zero suppression, there can be multiple occurences for
    # a given channel.  Each item in this array is a dictionary that will be
    # returned.
    occurences = []

    # trigger time tag
    ttt = get_trigger_time_tag(data) - offset

    number_of_channels_in_digitizer = 8

    check_header(data)

    pnt =  1

    word_chan_mask = get_word_by_index(data, pnt, False)
    chan_mask = word_chan_mask & 0xFF
    pnt += 3

    max_time = None

    for j in range(number_of_channels_in_digitizer):
        if ((chan_mask>>j)&1):
            current_channel = j
        else:
            print("Skipping channel", j)
            continue

        words_in_channel_payload = get_word_by_index(data, pnt, False)

        pnt += 1

        counter_within_channel_payload = 2
        wavecounter_within_channel_payload = 0

        while ( counter_within_channel_payload <= words_in_channel_payload ):
            word_control = get_word_by_index(data, pnt, False)

            if (word_control >> 28) == 0x8:
                this_occurence = {'samples': [],
                                  'channel': j,
                                  'module' : module,
                                  'time_start' : ttt + wavecounter_within_channel_payload}


                num_words_in_channel_payload = word_control & 0xFFFFFFF
                pnt = pnt + 1
                counter_within_channel_payload = counter_within_channel_payload + 1

                for k in range(num_words_in_channel_payload):
                    double_sample = get_word_by_index(data, pnt, False)
                    sample_1 = double_sample & 0xFFFF
                    sample_2 = (double_sample >> 16) & 0xFFFF

                    sample_1 = sample_1 * -1 + MAX_ADC_VALUE # TODO: do this elsewhere?
                    sample_2 = sample_2 * -1 + MAX_ADC_VALUE

                    this_occurence['samples'].append(sample_1)
                    this_occurence['samples'].append(sample_2)

                    pnt = pnt + 1
                    wavecounter_within_channel_payload = wavecounter_within_channel_payload + 2
                    counter_within_channel_payload = counter_within_channel_payload + 1

                this_occurence['time_end'] = ttt + wavecounter_within_channel_payload # off by 1?
                this_occurence['samples'] = np.array(this_occurence['samples'], dtype=SAMPLE_TYPE)
                if max_time == None or wavecounter_within_channel_payload > max_time:
                    max_time = wavecounter_within_channel_payload

                occurences.append(this_occurence)

            else:
                wavecounter_within_channel_payload += 2 * words_in_channel_payload + 1
                pnt = pnt + 1
                counter_within_channel_payload = counter_within_channel_payload + 1

    print('max time', max_time)
    return occurences


