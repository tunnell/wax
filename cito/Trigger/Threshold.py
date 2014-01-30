__author__ = 'tunnell'

import numpy as np
import scipy
from scipy import signal
import logging


def trigger(indecies, samples):
    peaks = []

    if len(indecies) == len(samples) == 0:
        return []

    i_start = 0
    index_last = None
    for i, index in enumerate(indecies):
        if index_last == None or (index - index_last) == 1:
            index_last = index_last
        elif index <= index_last:
            raise ValueError(
                "Indecies must be monotonically increasing: %d, %d!",
                index,
                index_last)
        elif index - index_last > 1:
            high_extrema = find_peaks(samples[i_start:i - 1])
            for value in high_extrema:
                peaks.append(value)
            i_start = i
        else:
            raise RuntimeError()

    if i_start < (len(indecies) - 1):  # If events still to process
        high_extrema = find_peaks(samples[i_start:-1])
        for value in high_extrema:
            peaks.append(value)

    return peaks


def find_peaks(values, threshold=10000, cwt_width=100):
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
    logging.debug('peak')
    logging.debug(peakind)
    logging.debug(values[peakind])
    logging.debug(max(values))
    peaks_over_threshold = peakind #[x for x in peakind if values[x] > threshold]
    return np.array(peaks_over_threshold, dtype=np.uint32)
