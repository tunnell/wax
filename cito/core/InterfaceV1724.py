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
"""Interface to Caen V1724

Flash ADC board.  There are many Cython wrappers, which means that the code
can be compiled.
"""

import numpy as np

# Samples are actually 14 bit unsigned, so 16 bit signed fine
SAMPLE_TYPE = np.int16
MAX_ADC_VALUE = 2 ** 14   # 14 bit ADC samples
SAMPLE_TIME_STEP = 1    # 10 ns

N_CHANNELS_IN_DIGITIZER = 8  # number of channels in digitizer board



def check_header(data, do_checks=True):
    """Check data header for control bits.

    Throws exception if misformated header.
    """
    word = data[0]
    print(data)
    if do_checks:
        assert word >> 20 == 0xA00, 'Data header misformated %s' % hex(word)
    return True


def get_block_size(data, do_checks=True):
    """Get size of block from header.
    """
    check_header(data, do_checks)
    word = data[0]
    size = (word & 0x0FFFFFFF)  # size in words
    if do_checks:
        # len(data) is in bytes, word = 4 bytes
        assert size == (len(data)),\
            'Size from header not equal to data size'

    return size  # number of words


def get_trigger_time_tag(data):
    check_header(data)
    word = data[3]

    # The trigger time is a 31 bit number.  The 32nd bit is pointless since it
    # is zero for the first clock cycle then 1 for each cycle afterward.  This
    # information from from Dan Coderre (Bern).  28/Aug/2013.
    word = word & 0x7FFFFFFF

    return word


def get_waveform(data, n_samples):
    # Each 'occurence' is a continous sequence of ADC samples for a given
    # channel.  Due to zero suppression, there can be multiple occurences for
    # a given channel.  Each item in this array is a dictionary that will be
    # returned.

    check_header(data)

    pnt = 1

    word_chan_mask = data[pnt]
    word_chan_mask = word_chan_mask & 0xFF
    pnt += 3

    data_to_return = []

    for j in range(N_CHANNELS_IN_DIGITIZER):
        samples = np.zeros(n_samples, dtype=SAMPLE_TYPE)
        indecies = np.zeros(n_samples, dtype=np.uint32)
        index = 0

        if ((word_chan_mask >> j) & 1):
            words_in_channel_payload = data[pnt]

            pnt += 1

            counter_within_channel_payload = 2
            wavecounter_within_channel_payload = 0

            while (counter_within_channel_payload <= words_in_channel_payload):
                word_control = data[pnt]

                if (word_control >> 28) == 0x8:
                    num_words_in_channel_payload = word_control & 0xFFFFFFF
                    pnt = pnt + 1
                    counter_within_channel_payload += 1

                    for k in range(num_words_in_channel_payload):
                        double_sample = data[pnt]

                        # the 32nd, 31st, 15th, and 16th bits should be zero
                        assert (
                            double_sample & 0x0C000C000) == 0, "Sample format incorrect"

                        sample_1 = double_sample & 0xFFFF
                        sample_2 = (double_sample >> 16) & 0xFFFF

                        samples[index] = sample_1
                        indecies[index] = wavecounter_within_channel_payload
                        wavecounter_within_channel_payload += 1
                        index += 1

                        samples[index] = sample_2
                        indecies[index] = wavecounter_within_channel_payload
                        wavecounter_within_channel_payload += 1
                        index += 1

                        pnt = pnt + 1
                        counter_within_channel_payload += 1
                else:
                    wavecounter_within_channel_payload += 2 * \
                        words_in_channel_payload + 1
                    pnt = pnt + 1
                    counter_within_channel_payload += 1

        else:
            #print('skipping', j)
            pass

        samples -= 2 ** 14
        samples *= -1

        # compress here
        if index != 0:
            samples = np.compress(index * [True], samples)
            indecies = np.compress(index * [True], indecies)
        else:
            samples = np.array([], dtype=SAMPLE_TYPE)
            indecies = np.array([], dtype=np.uint64)

        data_to_return.append((j, samples, indecies))

    return data_to_return
