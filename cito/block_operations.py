import pymongo
import time
import numpy as np
import snappy
#import cy_break_block
from scipy import signal

#if current_channel not in results:
# Samples are actually 14 bit
SAMPLE_TYPE = np.uint16
# 14 bit ADC samples
MAX_ADC_VALUE = 2**14

def get_word(data):
    word_size_in_bytes = 4

    number_of_words = int(len(data) / word_size_in_bytes)
    for i in range(number_of_words):
        yield get_word_by_index(data, i)

def get_word_by_index(data, i):
    word_size_in_bytes = 4

    if i > int(len(data)/4):
        return None

    i0 = i*word_size_in_bytes
    i1 = (i+1)*word_size_in_bytes

    word = int.from_bytes(data[i0:i1],'little')

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

    word_chan_mask = get_word_by_index(data, pnt)
    chan_mask = word_chan_mask & 0xFF
    pnt += 3

    for j in range(number_of_channels_in_digitizer):
        if ((chan_mask>>j)&1):
            current_channel = j
        else:
            print("Skipping channel", j)
            continue

        words_in_channel_payload = get_word_by_index(data, pnt)

        pnt += 1

        counter_within_channel_payload = 2
        wavecounter_within_channel_payload = 0

        while ( counter_within_channel_payload <= words_in_channel_payload ):
            word_control = get_word_by_index(data, pnt)

            if (word_control >> 28) == 0x8:
                this_occurence = {'samples': [],
                                  'channel': j,
                                  'module' : module,
                                  'time_start' : ttt + wavecounter_within_channel_payload}


                num_words_in_channel_payload = word_control & 0xFFFFFFF
                pnt = pnt + 1
                counter_within_channel_payload = counter_within_channel_payload + 1

                for k in range(num_words_in_channel_payload):
                    double_sample = get_word_by_index(data, pnt)
                    sample_1 = double_sample & 0xFFFF
                    sample_2 = (double_sample >> 16) & 0xFFFF

                    sample_1, sample_2 = [x * -1 + MAX_ADC_VALUE for x in [sample_1, sample_2]]

                    this_occurence['samples'].append(sample_1)
                    this_occurence['samples'].append(sample_2)

                    pnt = pnt + 1
                    wavecounter_within_channel_payload = wavecounter_within_channel_payload + 2
                    counter_within_channel_payload = counter_within_channel_payload + 1

                this_occurence['time_end'] = ttt + wavecounter_within_channel_payload # off by 1?
                occurences.append(this_occurence)

            else:
                if word_control != 0xFFFFFFFF:
                    wavecounter_within_channel_payload += 2 * words_in_channel_payload + 1
                    pnt = pnt + 1
                    counter_within_channel_payload = counter_within_channel_payload + 1
                else:
                    raise("Fuckup")

    return occurences

def invert_pulses(results):
    # 14 bit ADC samples
    max_adc_value = 2**14
    for key in results:
        results[key]['samples'] = results[key]['samples'] * -1 + max_adc_value
    return results

def sum_pulses(results, combined_data):
    for result in results:
        #combined_data[]
        time_start = result['time_start']

        for i, sample in enumerate(result['samples']):
            combined_data[time_start + i] = sample

    return combined_data

def find_peak(x, y):
    peakind = signal.find_peaks_cwt(y, np.array([100]))

    threshold = 10000
    peaks = []

    for a, b in zip(x[peakind], y[peakind]):
        if b > threshold:
            peaks.append(a)
    
    return np.array(peaks)


def process(data, module, snappy=False, offset=0):
    if snappy:
        data = snappy.uncompress(data)
    #print('ttt', get_trigger_time_tag(data))

    #t0 = time.time()
    #results = cy_break_block.get_waveform(data)
    #t1 = time.time()
    results = get_waveform(data, module, offset)
    #t2 = time.time()
    #print('Cython', t1-t0, 'Python', t2-t1)
    return results



if __name__ == "__main__":
    c = pymongo.MongoClient()
    db = c.data
    collection = db.test
    


    for doc in collection.find({'block_splitting' : 'todo'}):
                                        #update= {'$set' : {'block_splitting' : 'in_progress'}})
        if 'data' in doc:
            results = process(doc)
            collection.insert(results)
        else:
            print(doc)

        #collection.save(doc)


