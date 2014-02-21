"""Perform operations on sets of blocks
"""

import logging

import numpy as np

from cito.core import XeDB

# Samples are actually 14 bit unsigned, so 16 bit signed fine
SAMPLE_TYPE = np.int16
MAX_ADC_VALUE = 2 ** 14  # 14 bit ADC samples


def get_samples(data):
    # Parse data
    if len(data) > 32000:
        raise ValueError('Data from board larger than memory on board')

    samples = np.frombuffer(data, dtype=SAMPLE_TYPE)

    # Todo: make this a flag?
    if np.max(samples) >= MAX_ADC_VALUE or np.min(samples) < 0:
        raise ValueError('Corrupt data since more than 14 bits used')

    # Sanity check
    for i in range(len(data)):
        # the 32nd, 31st, 15th, and 16th bits should be zero
        assert (int(data[i]) & 0x0C000C000) == 0, "Sample format incorrect"

    # Invert pulse so larger energy deposit is larger ADC values
    samples *= -1
    samples += MAX_ADC_VALUE

    return samples


def get_data_and_sum_waveform(cursor):
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
            samples = get_samples(data)
        except:
            logging.exception('Failed to parse document: %s' % str(doc['_id']))
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

            interpreted_data[key] = {'indices': np.arange(time_correction, time_correction + samples.size),
                                     'samples': samples}

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
    interpreted_data[key] = {'indices': new_indices,
                             'samples': new_samples}

    return interpreted_data, size
