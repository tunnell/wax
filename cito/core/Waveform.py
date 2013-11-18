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

from cito.core import XeDB
from cito.core import InterfaceV1724


def get_pmt_number(num_board, num_channel):
    channels_per_board = 8 # this used elsewhere?
    if num_board == 770:
        scale = 0
    elif num_board == 876:
        scale = 1
    else:
        raise ValueError('Bad module number %d' % num_board)
    return channels_per_board * scale + num_channel


def get_data_and_sum_waveform(cursor, n_samples):
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
    log = logging.getLogger(__name__)

    size = 0

    interpreted_data = {}

    # This gets formatted later into something usable
    sum_data = {}  # index -> sample

    for doc in cursor:
        log.debug('Processing doc %s', str(doc['_id']))
        data = XeDB.get_data_from_doc(doc)
        num_board = doc['module']

        size += len(data)

        time_correction = doc['triggertime']

        this_board = InterfaceV1724.get_waveform(data, n_samples)

        for num_channel, samples, indecies in this_board:
            indecies += time_correction

            # Compute baseline with first 3 and last 3 samples
            baseline = np.concatenate([samples[0:3], samples[-3:-1]]).mean()#

            # i is for what is returned by get_waveform
            # sample_index is the index in detector time
            for i, sample_index in enumerate(indecies):
                sample = np.min((samples[i] - baseline), 0)

                if sample_index in sum_data:
                    sum_data[sample_index] += sample
                else:
                    sum_data[sample_index] = sample

            if indecies.size != 0:
                start, stop = np.min(indecies), np.max(indecies)

                num_pmt = get_pmt_number(num_board, num_channel)

                interpreted_data[(start, stop, num_pmt)] = {'indecies' : indecies,
                                                            'samples' : samples}

    log.debug("Size of data process in bytes: %d", size)
    if size == 0:
        return interpreted_data, size
    new_indecies = [x for x in sum_data.keys()]
    new_indecies.sort()
    new_samples = [sum_data[x] for x in new_indecies]
    new_indecies = np.array(new_indecies, dtype=np.int64)
    new_samples = np.array(new_samples, dtype=np.int32)

    interpreted_data[(np.min(new_indecies), np.max(new_indecies), 'sum')] = {'indecies' : new_indecies,
                                                                 'samples' : new_samples}



    return interpreted_data, size
