# cito - The Xenon1T experiments software trigger
# Copyright 2013.  All rights reserved.
# https://github.com/tunnell/cito
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of the Xenon experiment, nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Interface to Caen V1724 using Cython

Flash ADC board
"""

#cython: boundscheck=False
#cython: wraparound=False

import numpy as np
cimport numpy as np

import pyximport


np.import_array()

SAMPLE_TYPE = np.uint16 # Samples are actually 14 bit
MAX_ADC_VALUE = 2 ** 14   # 14 bit ADC samples
SAMPLE_TIME_STEP = 1    # 10 ns
WORD_SIZE_IN_BYTES = 4  # 4 bytes in a 32 bit word
N_CHANNELS_IN_DIGITIZER = 8 # number of channels in digitizer board


def get_word(data):
    """Generator for words
    """
    word_size_in_bytes = 4

    number_of_words = int(len(data) / word_size_in_bytes)
    for i in range(number_of_words):
        yield get_word_by_index(data, i)


def get_word_by_index(data, i):
    """Get 32-bit word by index

    This function is called often so be sure to check
    """
    cdef Py_ssize_t i0, i1
    i0 = i*WORD_SIZE_IN_BYTES
    i1 = (i+1)*WORD_SIZE_IN_BYTES

    cdef unsigned int word
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

def get_waveform(data, Py_ssize_t n_samples):
    """Fetch waveform

    :param data: data to analyze
    :param n_samples:   Max number of samples (overestimate!)
    :return: samples
    """
    # trigger time tag
    cdef unsigned int word_chan_mask, chan_mask, sample_1, sample_2

    check_header(data)

    cdef Py_ssize_t j, k, wavecounter_within_channel_payload, N_CHANNELS_IN_DIGITIZER, words_in_channel_payload, num_words_in_channel_payload
    cdef Py_ssize_t counter_within_channel_payload
    cdef Py_ssize_t pnt =  1

    word_chan_mask = get_word_by_index(data, pnt)
    chan_mask = word_chan_mask & 0xFF
    pnt += 3

    cdef np.ndarray[np.uint16_t, ndim=2] samples = np.zeros((N_CHANNELS_IN_DIGITIZER, n_samples),
                                                            dtype=SAMPLE_TYPE)

    # Max time seen, which is used for resizing the samples array
    cdef Py_ssize_t max_time

    for j in range(N_CHANNELS_IN_DIGITIZER):
        words_in_channel_payload = get_word_by_index(data, pnt)

        pnt += 1

        counter_within_channel_payload = 2
        wavecounter_within_channel_payload = 0

        while ( counter_within_channel_payload <= words_in_channel_payload ):
            word_control = get_word_by_index(data, pnt)

            if (word_control >> 28) == 0x8:
                num_words_in_channel_payload = word_control & 0xFFFFFFF
                pnt = pnt + 1
                counter_within_channel_payload = counter_within_channel_payload + 1

                for k in range(num_words_in_channel_payload):
                    double_sample = get_word_by_index(data, pnt, False)
                    sample_1 = double_sample & 0xFFFF
                    sample_2 = (double_sample >> 16) & 0xFFFF

                    samples[j][wavecounter_within_channel_payload] = sample_1
                    wavecounter_within_channel_payload += 1

                    samples[j][wavecounter_within_channel_payload] = sample_2
                    wavecounter_within_channel_payload += 1

                    print('samples', sample_1, sample_2)

                    pnt = pnt + 1
                    counter_within_channel_payload = counter_within_channel_payload + 1

                if wavecounter_within_channel_payload > max_time:
                    max_time = wavecounter_within_channel_payload

            else:
                wavecounter_within_channel_payload += 2 * words_in_channel_payload + 1
                pnt = pnt + 1
                counter_within_channel_payload = counter_within_channel_payload + 1


    # This drops off any zeros at the rightward colums
    samples = np.compress(max_time * [True], samples, axis=1)

    return samples




