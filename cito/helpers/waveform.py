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
"""Perform operations on sets of blocks
"""

import logging

import numpy as np
from scipy import signal
import scipy

from cito.helpers import xedb
from cito.helpers import InterfaceV1724


def find_peaks_in_data(indecies, samples):
    peaks = []

    if len(indecies) == len(samples) == 0:
        return []

    i_start = 0
    index_last = None
    for i, index in enumerate(indecies):
        if index_last == None or (index - index_last) == 1:
            index_last = index_last
        elif index <= index_last:
            raise ValueError("Indecies must be monotonically increasing: %d, %d!",
                             index,
                             index_last)
        elif index - index_last > 1:
            high_extrema = find_peaks(samples[i_start:i-1])
            for value in high_extrema:
                peaks.append(value)
            i_start = i
        else:
            raise RuntimeError()

    if i_start < (len(indecies) - 1):  #If events still to process
        high_extrema = find_peaks(samples[i_start:-1])
        for value in high_extrema:
            peaks.append(value)

    return peaks




def find_peaks(values, threshold=10000, cwt_width=20):
    """Find peaks within list of values.

    Uses scipy to find peaks above a threshold.

    Args:
        values (list):  The 'y' values to find a peak in.
        threshold (int): Threshold in ADC counts required for peaks.
        cwt_width (float): The width of the wavelet that is convolved

    Returns:
       np.array: Array of peak indecies

    """

    # 20 is the wavelet width
    peakind = scipy.signal.find_peaks_cwt(values, np.array([cwt_width]))
    peaks_over_threshold = [x for x in peakind if values[x] > threshold]
    return np.array(peaks_over_threshold, dtype=np.uint32)


def save_time_range(size, peaks,
                    range_around_trigger = (-10, 10)):
    """
    There should be no wrap around.
    """
    # Bureaucracy
    log = logging.getLogger('waveform')
    if not isinstance(size, int):
        raise ValueError('Size must be int')
    if isinstance(peaks, int):
        peaks = [peaks]
    elif isinstance(peaks, float):
        raise ValueError("peaks must be a list of integers (i.e., not a float)")

    # Physics
    to_save = np.zeros(size, dtype=np.bool)
    for peak in peaks:
        log.debug('Flagging peak around %d' % peak)


        # The 'min' and 'max' are used to prevent wrap around
        this_range = np.arange(max(peak + range_around_trigger[0], 0),
                               min(peak + range_around_trigger[1], size))

        #  'True' is set for every index in 'this_range'
        to_save[this_range] = True

    log.debug('Save range: ', to_save)

    return to_save

def get_sum_waveform(cursor, offset, n_samples):
    """Get inverted sum waveform from mongo

    Args:
        cursor (iterable):  An iterable object of documents containing Caen
                           blocks.  This can be a pymongo Cursor.
        offset (int): An integer start time
        n_samples (int): How many samples to store


    Returns:
       dict: Results dictionary with key 'size' and 'occurences'

    Todo: go through and check all the types
      - Longer int since summing many, otherwise wrap around.
      - use 8 bit and divide by num channels?  combine adjacent?

    """
    log = logging.getLogger('waveform')

    # dividie by some nubmer
    log.debug('Number of samples for sum waveform: %d', n_samples)

    size = 0

    sum_data = {}  # index -> sample

    for doc in cursor:
        data = xedb.get_data_from_doc(doc)
        size += len(data)

        time_correction = doc['triggertime'] - offset

        this_board = InterfaceV1724.get_waveform(data, n_samples)

        for channel, samples, indecies in this_board:
            indecies += time_correction

            # Compute baseline with first 3 and last 3 samples
            baseline = np.concatenate([samples[0:3], samples[-3:-1]]).mean()#
            print(channel, np.concatenate([samples[0:3], samples[-3:-1]]))

            # i is for what is returned by get_waveform
            # sample_index is the index in detector time
            for i, sample_index in enumerate(indecies):
                sample = np.min((samples[i] - baseline), 0)
                #print('\t', samples[i], sample, np.concatenate([samples[0:3], samples[-3:-1]]).mean())
                if(samples[i] < 0.0):
                    print(i, sample_index, samples[i], baseline)
                    raise ValueError()

                if sample_index in sum_data:
                    sum_data[sample_index] += sample
                else:
                    sum_data[sample_index] = sample


    new_indecies = list(sum_data.keys())
    new_indecies.sort()

    new_samples = [sum_data[x] for x in new_indecies]

    log.info("Size of data process in bytes: %d", size)

    results = {}
    results['size'] = size
    results['indecies'] =  np.array(new_indecies, dtype=np.int32)
    results['samples'] = np.array(new_samples, dtype=np.int32)

    return results
