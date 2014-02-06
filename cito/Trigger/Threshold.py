__author__ = 'tunnell'

import numpy as np
import scipy
from scipy import signal
import logging
import numpy as np
from scipy.signal._peak_finding import _filter_ridge_lines, _identify_ridge_lines
from scipy.lib.six.moves import xrange
from scipy.signal.wavelets import cwt, ricker
from scipy.stats import scoreatpercentile
import time

def trigger(indices, samples):
    peaks = []

    if len(indices) == len(samples) == 0:
        return []

    i_start = 0
    index_last = None
    for i, index in enumerate(indices):
        if index_last == None or (index - index_last) == 1:
            index_last = index_last
        elif index <= index_last:
            raise ValueError(
                "Indices must be monotonically increasing: %d, %d!",
                index,
                index_last)
        elif index - index_last > 1:
            high_extrema = find_peaks(samples[i_start:i - 1])
            for value in high_extrema:
                peaks.append(value)
            i_start = i
        else:
            raise RuntimeError()

    if i_start < (len(indices) - 1):  # If events still to process
        high_extrema = find_peaks(samples[i_start:-1])
        for value in high_extrema:
            peaks.append(value)

    return peaks

def cwt(data, wavelet, widths):
    output = np.zeros([len(widths), len(data)])
    for ind, width in enumerate(widths):
        wavelet_data = wavelet(min(10 * width, len(data)), width)
        output[ind, :] = signal.fftconvolve(data, wavelet_data,
                                              mode='same')
    return output

def find_peaks_cwt(vector, widths, wavelet=None, max_distances=None, gap_thresh=None,
                   min_length=None, min_snr=1, noise_perc=10):
    """Stolen from Scipy"""
    if gap_thresh is None:
        gap_thresh = np.ceil(widths[0])
    if max_distances is None:
        max_distances = widths / 4.0
    if wavelet is None:
        wavelet = ricker

    cwt_dat = cwt(vector, wavelet, widths)
    ridge_lines = _identify_ridge_lines(cwt_dat, max_distances, gap_thresh)
    filtered = _filter_ridge_lines(cwt_dat, ridge_lines, min_length=min_length,
                                   min_snr=min_snr, noise_perc=noise_perc)
    max_locs = [x[1][0] for x in filtered]
    return sorted(max_locs)


def find_peaks(values, threshold=200, cwt_width=100):
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
    logging.debug('CWT with n=%d' % values.size)
    t0 = time.time()
    peakind = find_peaks_cwt(values, np.array([cwt_width]))
    peaks_over_threshold = peakind # [x for x in peakind if values[x] > threshold]
    t1 = time.time()

    logging.debug('Convolution duration: %f s' % (t1 - t0))
    return np.array(peaks_over_threshold, dtype=np.uint32)
