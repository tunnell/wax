"""Perform operations on sets of blocks
"""

import logging

import numpy as np

# Samples are actually 14 bit unsigned, so 16 bit signed fine
SAMPLE_TYPE = np.int16
MAX_ADC_VALUE = 2 ** 14  # 14 bit ADC samples


def get_samples(data):
    # Parse data
    if len(data) > 32000:
        raise ValueError('Data from board larger than memory on board')

    samples = np.frombuffer(data, dtype=SAMPLE_TYPE)

    # Invert pulse so larger energy deposit is larger ADC values
    samples *= -1
    samples += MAX_ADC_VALUE

    return samples


def get_data_and_sum_waveform(cursor, inputdb):
    """Get inverted sum waveform from mongo

    Args:
        cursor (iterable):  An iterable object of documents containing Caen
                           blocks.  This can be a pymongo Cursor.
        inputdb - class


    Returns:
       dict: Results dictionary with key 'size' and 'occurences'
    """
    log = logging.getLogger(__name__)

    size = 0

    interpreted_data = {}

    # This gets formatted later into something usable
    sum_data = {}  # index -> sample

    for doc in cursor:
        data = inputdb.get_data_from_doc(doc)
        num_channel = doc['channel']
        if doc['module'] != -1:
            num_channel = doc['module'] * 10 + doc['channel']

        size += len(data)

        time_correction = doc['time']

        try:
            samples = get_samples(data)
        except ValueError as e:
            logging.error('Failed to parse document: %s' % str(doc['_id']))
            logging.exception(e)
            continue

        # Improve?
        # Compute baseline with first 3 - numpy function slow
        baseline = (samples[0] + samples[1] + samples[2])/3
        samples -= baseline

        reduction_factor = 100

        for i, sample in enumerate(samples):
            sample_index = int((time_correction + i)/reduction_factor)

            if sample_index in sum_data:
                sum_data[sample_index] += sample
            else:
                sum_data[sample_index] = np.int32(sample)

        if samples.size != 0:
            key = (time_correction,
                   time_correction + len(samples),
                   num_channel)

            interpreted_data[key] = {
                'indices': np.arange(time_correction,
                                     time_correction + samples.size,
                                     dtype=np.int32),
                'samples': samples}

    log.debug("Size of data process in bytes: %d", size)
    if size == 0:
        return interpreted_data, size
    new_indices = [x for x in sum_data.keys()]
    new_indices.sort()
    new_samples = [sum_data[x] for x in new_indices]
    new_indices = np.array(new_indices, dtype=np.int32) * reduction_factor
    new_samples = np.array(new_samples, dtype=np.int32)

    if new_indices.size >= 2:
        key = (new_indices[0],
               new_indices[-1],
               'sum')
        interpreted_data[key] = {'indices': new_indices,
                                 'samples': new_samples}

    return interpreted_data, size
