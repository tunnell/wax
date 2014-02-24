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

import scipy
import numpy as np
from scipy.signal import butter
from scipy.signal import filtfilt

from cito.core.math import merge_subranges, find_subranges


CWT_WIDTH = 50
MAX_DRIFT = 18000


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
    combined_ranges = merge_subranges(ranges, indices, MAX_DRIFT)

    logging.info("Combined ranges: %s" % str(combined_ranges))

    for s in combined_ranges:
        subsamples = samples[s[0]:s[1]]

        high_extrema, trigger_meta_data = find_peaks(subsamples, 10)
        for value in high_extrema:
            peaks.append(value)

        smoothed_sum[s[0]:s[1]] = trigger_meta_data['smooth']

    return peaks, smoothed_sum


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
    logging.info('Filtering with n=%d' % values.size)
    t0 = time.time()
    gap_thresh = np.ceil(widths[0])
    max_distances = widths / 4.0

    b, a = butter(3, 0.05, 'low')

    # Forward backward filter
    smooth_data = filtfilt(b, a, values)

    # The identification and filtering of ridge lines expect a 2D image, but
    # our data is 1D.  Therefore, we reshape the smooth_data array.
    #smooth_data = np.reshape(smooth_data, (1, smooth_data.size))
    max_locs = scipy.signal.argrelmax(smooth_data)[0]

    #ridge_lines = _identify_ridge_lines(smooth_data, max_distances, gap_thresh)
    #filtered = _filter_ridge_lines(smooth_data, ridge_lines, min_length=None,
    #                               min_snr=1, noise_perc=10)
    #max_locs = [x[1][0] for x in filtered]
    logging.error(max_locs)
    trigger_meta_data = {}
    trigger_meta_data['smooth'] = smooth_data[0]
    #trigger_meta_data['ridge_lines'] = ridge_lines
    #trigger_meta_data['filtered'] = filtered

    peakind = sorted(max_locs)

    peaks_over_threshold = [x for x in peakind if values[x] > threshold]
    t1 = time.time()

    logging.info('Filtering duration: %f s' % (t1 - t0))
    return np.array(peaks_over_threshold, dtype=np.uint32), trigger_meta_data







