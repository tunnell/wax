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
        num_channel = doc['module']

        size += len(data)

        time_correction = doc['triggertime']

        try:
            samples = InterfaceV1724.get_samples(data)
        except:
            logging.exception('Failed to parse document: %s' % str(doc))
            continue

        # Improve?
        # Compute baseline with first 3 and last 3 samples
        baseline = np.concatenate([samples[0:3], samples[-3:-1]]).mean()

        for i, sample in enumerate(samples):
            sample = np.min((samples[i] - baseline), 0)
            sample_index = time_correction + i

            if sample_index in sum_data:
                sum_data[sample_index] += sample
            else:
                sum_data[sample_index] = sample


        if samples.size != 0:
            key = (time_correction,
                   time_correction + len(samples),
                   num_channel)

            interpreted_data[key] = {'indices' : np.arange(time_correction, time_correction + samples.size),
                                     'samples' : samples}

    log.debug("Size of data process in bytes: %d", size)
    if size == 0:
        return interpreted_data, size
    new_indices = [x for x in sum_data.keys()]
    new_indices.sort()
    new_samples = [sum_data[x] for x in new_indices]
    new_indices = np.array(new_indices, dtype=np.int64)
    new_samples = np.array(new_samples, dtype=np.int32)

    key = (new_indices[0],
           new_indices[-1],
           'sum')

    #  Here, we store indices as well as the range (in the key) because
    # the samples of the sum waveform need not be contigous
    interpreted_data[key] = {'indices' : new_indices,
                             'samples' : new_samples}

    return interpreted_data, size
