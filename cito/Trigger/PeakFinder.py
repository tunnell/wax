"""Find a peak in sum waveform

Given a list of ADC sample values, the peaks are found.   There are two
functions defined in this class.  The first is:

 identify_nonoverlapping_trigger_windows

which is allows the peak finder to run on multiple spacially seperate trigger
 windows at once.  The actual logic of the peak finder is in:

 find_peaks

where, for example, filtering and identification of ridge lines is performed.
"""

__author__ = 'tunnell'

import logging
import time

import numpy as np

from cito.core.math import merge_subranges, find_subranges


CWT_WIDTH = 50  # units of 10 ns
MAX_DRIFT = 18000  # units of 10 ns


def identify_nonoverlapping_trigger_windows(indices, samples):
    """Find peaks within contigous ranges

    Within continous subranges, find peaks above threshold.  This is typically the entry point into this
    module.
    """

    smoothed_sum = np.zeros_like(indices)

    peaks = []  # Store the indices of peaks

    # find_subranges returns the LOCATION within the array; not the value.
    # This is required because we need to use these later to find what samples
    # these correspond to.
    ranges = find_subranges(indices)

    # Combine any ranges within max_drift, which requires having indices
    # so we know what 'ranges' means.  Once again, what is returned
    # is locations within the array.  This is used later so we know where
    # samples are.
    combined_ranges = merge_subranges(ranges, indices, MAX_DRIFT / 2)

    logging.debug("Combined ranges: %s" % str(combined_ranges))

    for s in combined_ranges:
        subsamples = samples[s[0]:s[1]]

        high_extrema, trigger_meta_data = find_peaks(subsamples)
        for value in high_extrema:
            peaks.append(s[0] + value)

        smoothed_sum[s[0]:s[1]] = trigger_meta_data['smooth']

    return np.array(peaks, dtype=np.int64), smoothed_sum


def find_peaks(values, threshold=1000, widths=np.array([CWT_WIDTH])):
    """Find peaks within list of values.

    Use the butter filter, then perform a forward-backward filter such that
    no offset is introduced.

    Args:
        values (list):  The 'y' values to find a peak in.
        threshold (int): Threshold in ADC counts required for peaks.
        cwt_width (float): The width of the wavelet that is convolved

    Returns:
       np.array: Array of peak indices

    """

    # 20 is the wavelet width
    logging.debug('Filtering with n=%d' % values.size)
    t0 = time.time()
    r = 1
    n = len(values)
    values.resize((r, np.ceil(n/r)))
    smooth_data = values.sum(1)

    # Over threshold is an array of all indicies above threshold
    over_threshold = np.where(smooth_data > threshold)[0]

    # We don't want every sample above threshold, just the center of the range
    # above threshold.
    peaks = []
    for a, b in find_subranges(over_threshold):
        peaks.append(np.round(float(over_threshold[b] + over_threshold[a]) / 2))

    trigger_meta_data = {}
    trigger_meta_data['smooth'] = smooth_data
    trigger_meta_data['reduction_factor'] = r
    t1 = time.time()

    logging.debug('Filtering duration: %f s' % (t1 - t0))
    return np.array(peaks, dtype=np.int64), trigger_meta_data
