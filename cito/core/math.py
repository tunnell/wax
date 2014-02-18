from itertools import groupby
import logging
import numpy as np

__author__ = 'tunnell'


def compute_subranges(peaks, range_around_peak=(-18000, 18000)):
    """Determine overlapping ranges

    range_around_peak in units of 10 ns
    18000 means 180 us."""
    peaks.sort()

    assert len(range_around_peak) == 2
    assert range_around_peak[0] < range_around_peak[1]

    ranges = []

    for peak in peaks:
        time_start = peak + range_around_peak[0]
        time_stop = peak + range_around_peak[1]

        if len(ranges) >= 1 and time_start < ranges[-1][1]:  # ranges[-1] is latest range
            logging.debug('Combining time ranges:')
            logging.debug('\t%s' % (str((time_start, time_stop))))
            logging.debug('\t%s' % str(ranges[-1]))

            ranges[-1][1] = time_stop
        else:
            ranges.append([time_start, time_stop])

    return ranges


def merge_subranges(ranges, distance):
    """Ranges is a list of tuples, that are merged if less than distance between them
    """
    combined_ranges = []
    for subrange in ranges:
        if len(combined_ranges) == 0:
            combined_ranges.append(subrange)
        elif combined_ranges[-1][1] + distance > subrange[0]:
            combined_ranges[-1][1] = subrange[1]
        else:
            combined_ranges.append(subrange)
    return combined_ranges


def find_subranges(indices):
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

def overlap_region(range1, range2):

    a0, a1 = range1
    b0, b1 = range2

    # Overlap range
    range_overlap = (None, None)

    # If all of A is before B, or vice versa...
    if a1 < b0 or b1 < a0:  # If true, no overlap
        return range_overlap  # None, None
    elif a0 <= b0 and b1 <= a1:  #  All of B contained in A
        range_overlap = (b0, b1)
    elif b0 <= a0 and a1 <= b1:  #  All of A contained in B
        range_overlap = (a0, a1)
    else:
        logging.error("Partial overlap. slow")
        overlap = np.intersect1d(np.arange(a0, a1), np.arange(b0, b1))
        if overlap.size == 0:
            raise ValueError('No overlap found?... (%d, %d) (%d, %d) %s' % (a0, a1, b0, b1, str(a1 < b0)))
        range_overlap = (overlap[0], overlap[1])

    return range_overlap


def overlap(min1, max1, min2, max2):
    return max(0, min(max1, max2) - max(min1, min2))