import pymongo
import time
import binascii
import bitstring
import matplotlib.pyplot as plt
import numpy as np
import snappy
from scipy import signal

#if current_channel not in results:
# Samples are actually 14 bit
SAMPLE_TYPE = np.uint16

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
    word = bitstring.BitArray(bytes=data[i0:i1])
    word.byteswap(fmt='@L')
    return word

def check_header(data):
    word = get_word_by_index(data, 0)
    assert(word.startswith('0xa0'))

def get_event_size(data):
    check_header(data)
    word = get_word_by_index(data, 0)
    size = (word.uint & 0x0FFFFFFF)
    assert(size == int(len(data)/4))
    return size # number of words

def get_trigger_time_tag(data):
    check_header(data)
    word = get_word_by_index(data, 3)
    print('ttt', word, word.uint)

def get_waveform(data):
    results = {}

    pnt=0 
    current_channel = 0
    words_in_channel_payload = 0

    if get_word_by_index(data, pnt).startswith('0xa0'):
        pnt = pnt + 1

        word_chan_mask = get_word_by_index(data, pnt)
        chan_mask = word_chan_mask.uint & 0xFF
        pnt = pnt + 1

        word_evt_ctr = get_word_by_index(data, pnt)
        pnt = pnt + 1

        word_ttt = get_word_by_index(data, pnt)
        pnt = pnt + 1

        for j in range(8):
            if ((chan_mask>>j)&1):
                current_channel = j
            else:
                print("Skipping channel", j)
                continue

            words_in_channel_payload = get_word_by_index(data, pnt).uint
            #print('words_in_channel_payload', words_in_channel_payload)

            results[current_channel] = {'time': np.zeros(0,
                                                         dtype = SAMPLE_TYPE),
                                        'samples':np.zeros(0,
                                                           dtype = SAMPLE_TYPE) }
            
            pnt += 1
    
            counter_within_channel_payload = 2
            wavecounter_within_channel_payload = 0

            while ( counter_within_channel_payload <= words_in_channel_payload ):
                word_control = get_word_by_index(data, pnt)
                
                if word_control.startswith('0b1000'):
                    num_words_in_channel_payload = word_control.uint & 0xFFFFFFF
                    pnt = pnt + 1
                    counter_within_channel_payload = counter_within_channel_payload + 1
                    
                    for k in range(num_words_in_channel_payload):
                        double_sample = get_word_by_index(data, pnt)
                        sample_1 = double_sample.uint & 0xFFFF
                        sample_2 = (double_sample.uint >> 16) & 0xFFFF

                        results[current_channel]['time'] = np.append(results[current_channel]['time'],  wavecounter_within_channel_payload)
                        results[current_channel]['samples'] = np.append(results[current_channel]['samples'], sample_1)

                        results[current_channel]['time'] = np.append(results[current_channel]['time'],  wavecounter_within_channel_payload + 1)
                        results[current_channel]['samples'] = np.append(results[current_channel]['samples'], sample_2)

                        pnt = pnt + 1
                        wavecounter_within_channel_payload = wavecounter_within_channel_payload + 2
                        counter_within_channel_payload = counter_within_channel_payload + 1

                else:
                    if word_control.uint != 0xFFFFFFFF:
                        wavecounter_within_channel_payload += 2 * words_in_channel_payload + 1
                        pnt = pnt + 1
                        counter_within_channel_payload = counter_within_channel_payload + 1
                    else:
                        raise("Fuckup")


    else:
        print ("not starting with 0xa0?")

    return results

def invert_pulses(results):
    # 14 bit ADC samples
    max_adc_value = 2**14
    for key in results:
        results[key]['samples'] = results[key]['samples'] * -1 + max_adc_value
    return results

def sum_pulses(results):
    summed_waveform = {}

    for key in results:
        for t, Q in zip(results[key]['time'], results[key]['samples']):
            if t in summed_waveform:
                summed_waveform[t] += Q
            else:
                summed_waveform[t] = Q

    zipped_waveform = [(k, v) for k, v in summed_waveform.items()]
    x, y = zip(*zipped_waveform)
    return np.array(x, dtype = SAMPLE_TYPE), np.array(y, dtype = SAMPLE_TYPE)

def find_peak(x, y):
    peakind = signal.find_peaks_cwt(y, np.array([100]))

    threshold = 10000
    peaks = []

    for a, b in zip(x[peakind], y[peakind]):
        if b > threshold:
            peaks.append(a)
    
    return np.array(peaks)

c = pymongo.MongoClient()
db = c.data
collection = db.test

for timestamp in collection.distinct('triggertime'):
    print(timestamp)
    if timestamp == 0:
        continue
    global_results = {}
    for doc in collection.find({'triggertime' : timestamp}):
        print("Zip", doc['zipped'])
        #assert(doc['zipped'] is False)
        data = doc['data']
        if doc['zipped']:
            data = snappy.uncompress(data)
        get_trigger_time_tag(data)
        results = get_waveform(data)
        module = doc['module']

        results = invert_pulses(results)

        for key in results:
            global_results['%d_%d' % (module, key)] = results[key]
            
            
    plt.figure()
    for key in global_results:
        plt.plot(global_results[key]['time'], global_results[key]['samples'], label=key)

    x,y = sum_pulses(global_results)
    peaks = find_peak(x,y)
    plt.vlines(peaks, 20000, 50000, colors='red', linestyles='dashed', label='peak')

    plt.plot(x,y, 'o', label='sum')
    plt.xlabel('time [10 ns]')
    plt.ylabel('charge [adc counts]')
    plt.title('peak over threshold after CWT')
    plt.legend()
    plt.savefig('global.eps')
    
    break




#x,y = get_waveform(data)    
#plt.plot(x,y)
#plt.savefig('wf.eps')
#plt.show()

