__author__ = 'tunnell'

import logging
import time

from scipy import signal
import numpy as np
from scipy.signal._peak_finding import _filter_ridge_lines, _identify_ridge_lines
from scipy.signal.wavelets import ricker

from itertools import groupby

CWT_WIDTH = 150

def subranges(indices):
    """Identify groups of continuous numbers in a list

    For example, if indices is:

        [2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 20]

    Then the location within the list of continuous ranges are at:

        [(0,3), (4, 9), (10, 10)]

    """
    ranges = []
    for k, g in groupby(enumerate(indices), lambda i_x:i_x[0]-i_x[1]):
        # Each value is formated as: (location in array, value in array)
        values = list(g)

        # values[0] and values[-1] are range boundaries
        ranges.append([values[0][0], values[-1][0]])

    return ranges


def merge_subranges(cwt_width, ranges):
    combined_ranges = []
    for subrange in ranges:
        if len(combined_ranges) == 0:
            combined_ranges.append(subrange)
        elif combined_ranges[-1][1] + 2 * cwt_width > subrange[0]:
            combined_ranges[-1][1] = subrange[1]
        else:
            combined_ranges.append(subrange)
    return combined_ranges


def trigger(indices, samples):
    """Find peaks within contigous ranges

    Within continous subranges, find peaks above threshold.
    """

    cwt_width=50 # samples

    peaks = []  # Store the indices of peaks

    ranges = subranges(indices)
    combined_ranges = merge_subranges(cwt_width, ranges)

    logging.debug("Ranges: %s" % str(ranges))
    logging.debug("Combined ranges: %s" % str(combined_ranges))

    for subrange in combined_ranges:
        subsamples = samples[subrange[0]:subrange[1]]

        high_extrema = find_peaks(subsamples, cwt_width=cwt_width)
        for value in high_extrema:
            peaks.append(value)

    return peaks


def find_peaks(values, threshold=1000, cwt_width=CWT_WIDTH):
    """Find peaks within list of values.

    Uses scipy to find peaks above a threshold.

    Args:
        values (list):  The 'y' values to find a peak in.
        threshold (int): Threshold in ADC counts required for peaks.
        cwt_width (float): The width of the wavelet that is convolved

    Returns:
       np.array: Array of peak indices

    """

    # 20 is the wavelet width
    logging.debug('CWT with n=%d' % values.size)
    t0 = time.time()
    peakind = find_peaks_cwt(values, np.array([cwt_width]))
    peaks_over_threshold = [x for x in peakind if values[x] > threshold]
    t1 = time.time()

    logging.debug('Convolution duration: %f s' % (t1 - t0))
    return np.array(peaks_over_threshold, dtype=np.uint32)


def smooth(vector, widths=np.array([CWT_WIDTH])):
    """Smooth a vector

    Using a predefined width (which can be given as input), smooth the values
    in 'vector'.  Return a numpy array the length of vector, but smoothed.
    """
    width = widths[0]
    cwt_dat = np.zeros([1, len(vector)])
    wavelet = ricker
    wavelet_data = wavelet(min(10 * width, len(vector)), width)
    cwt_dat[0, :] = signal.fftconvolve(vector, wavelet_data,
                                       mode='same')
    return cwt_dat


def find_peaks_cwt(vector, widths=np.array([CWT_WIDTH])):
    """Find peaks

    Returns list of peaks and debbuging info."""
    gap_thresh = np.ceil(widths[0])
    max_distances = widths / 4.0

    cwt_dat = smooth(vector, widths)

    ridge_lines = _identify_ridge_lines(cwt_dat, max_distances, gap_thresh)
    filtered = _filter_ridge_lines(cwt_dat, ridge_lines, min_length=None,
                                   min_snr=1, noise_perc=10)
    max_locs = [x[1][0] for x in filtered]

    debugging_info = {}
    debugging_info['cwt'] = cwt_dat[0]
    debugging_info['ridge_lines'] = ridge_lines
    debugging_info['filtered'] = filtered

    return sorted(max_locs), debugging_info






