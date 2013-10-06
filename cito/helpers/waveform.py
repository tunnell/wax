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
from scipy.stats import norm
import scipy

from cito.helpers import xedb
from cito.helpers import InterfaceV1724Swig
from cito.helpers import InterfaceV1724
from cito.helpers import CaenBlockParsing


def filter_samples(values):
    """Apply a filter

    :rtype : dict
    :param values: Values to filter
    :type values: np.array
    """
    new_values = np.zeros_like(values)

    print('\tprefilter')
    my_filter = norm(0, 100)  # mu=0, sigma=100
    filter_values = 600 * [0.]
    for j in range(-300, 300):
        filter_values[j] = my_filter.pdf(j)

    print('\tapply_filter')
    for i in range(values.size):
        for j in range(-300, 300):
            if j > 0 and j < values.size:
                new_values += values[i] * filter_values[j]

    return new_values


def find_peaks(values, threshold=10000):
    """Find peaks within list of values.

    Uses scipy to find peaks above a threshold.

    Args:
        values (list):  The 'y' values to find a peak in.
        threshold (int): Threshold in ADC counts required for peaks.

    Returns:
       list: Peaks

    """
    extrema = scipy.signal.argrelmax(values)
    high_extrema = []
    for i in extrema:
        if values[i] > threshold:
            high_extrema.append(i)
    return high_extrema

#@profile
def get_sum_waveform(cursor, offset, n_samples):
    """Get inverted sum waveform from mongo

    Args:
        cursor (iterable):  An iterable object of documents containing Caen
                           blocks.  This can be a pymongo Cursor.
        offset (int): An integer start time
        n_samples (int): How many samples to store


    Returns:
       dict: Results dictionary with key 'size' and 'occurences'

    """
    log = logging.getLogger('waveform')
    # Longer int since summing many, otherwise wrap around.
    # TODO: check that unsigned 16 bit doesn't work?  Or bit shift (i.e. avg) or
    # dividie by some nubmer
    #log.debug('Number of samples for sum waveform: %d', n_samples)
    import time

    some_time = time.time()
    #occurences = np.zeros(n_samples, dtype=np.int16)
    #print('It took', (time.time() - some_time), 'to allocate memory')
    size = 0
    scale = 10 # how to scale samples
    assert CaenBlockParsing.setup_sum_waveform_buffer(n_samples);
    CaenBlockParsing.setup_return_buffer(10000)

    for doc in cursor:
        data = xedb.get_data_from_doc(doc)
        time_correction = doc['triggertime'] - offset

        temp_size = InterfaceV1724.get_block_size(data, False)

        #  2 bytes are a sample
        #result = InterfaceV1724Swig.get_waveform(data, )

        n = int(temp_size * 2)
        a = np.fromstring(data, dtype='uint32')

#        assert (len(data) != 0)
        CaenBlockParsing.inplace(a)
        CaenBlockParsing.put_samples_into_occurences(time_correction, scale)

        size += 4 * temp_size

    occurences = CaenBlockParsing.get_sum_waveform(n_samples)
    #print("size", size)
    #print('len', len(occurences[1]), n_samples)
    results = {}
    results['size'] = size
    results['occurences'] = occurences[1]
    #raise ValueError()
    #print(occurences)
    #print('sum', np.sum(occurences[1]))

    return results
