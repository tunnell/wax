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

        # ranges[-1] is latest range
        if len(ranges) >= 1 and time_start <= ranges[-1][1]:
            ranges[-1][1] = time_stop
        else:
            ranges.append([time_start, time_stop])

    return ranges


def merge_subranges(ranges, indices, distance):
    """Ranges is a list of tuples, that are merged if less than distance between them
    """
    combined_ranges = []
    for subrange in ranges:
        if len(combined_ranges) == 0:
            combined_ranges.append(subrange)
        elif indices[combined_ranges[-1][1]] + distance > indices[subrange[0]]:
            combined_ranges[-1][1] = subrange[1]
        else:
            combined_ranges.append(subrange)
    return combined_ranges

def group(L):
    last = L[0]
    ifirst = 0
    ilast = 0
    for i, n in enumerate(L[1:]):
        if n - 100 == last: # Part of the group, bump the end
            last = n
            ilast = i + 1
        else: # Not part of the group, yield current group and start a new
            yield [ifirst, ilast]
            last = n
            ifirst = ilast = i + 1
    yield [ifirst, ilast] # Yield the last group

def find_subranges(values):
    """Identify continuous ranges in a list and return their location.

    For example, if values is:

        [2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 20]

    Then the continuous ranges are at:

        [(0,3), (4, 9), (10, 10)]

    See http://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
    """
    if values.size == 0:
        return []

    return list(group(values))


def overlap_region(range1, range2):
    a0, a1 = range1
    b0, b1 = range2

    # Overlap range
    range_overlap = (None, None)

    # If all of A is before B, or vice versa...
    if a1 < b0 or b1 < a0:  # If true, no overlap
        return range_overlap  # None, None
    elif a0 <= b0 and b1 <= a1:  # All of B contained in A
        range_overlap = (b0, b1)
    elif b0 <= a0 and a1 <= b1:  # All of A contained in B
        range_overlap = (a0, a1)
    else:
        logging.error("Partial overlap. slow")
        overlap = np.intersect1d(np.arange(a0, a1), np.arange(b0, b1))
        if overlap.size == 0:
            raise ValueError(
                'No overlap found?... (%d, %d) (%d, %d) %s' % (a0, a1, b0, b1, str(a1 < b0)))
        range_overlap = (overlap[0], overlap[1])

    return range_overlap


def overlap(min1, max1, min2, max2):
    return max(0, min(max1, max2) - max(min1, min2))


def speed_in1d_continous(a, b, x, y):
    """A speedy version of numpy.in1d if dealing with ranges.

     We know that a <= b and x <= y

     Combinatorics: all permutations of (a, b, x, y) where x < y and a < b:

     Seperate:
         ('a', 'b', 'x', 'y')
         ('x', 'y', 'a', 'b')
    Embedded:
         ('x', 'a', 'b', 'y')
         ('a', 'x', 'y', 'b')
    Partially embedded:
         ('a', 'x', 'b', 'y')
         ('x', 'a', 'y', 'b')

    """

    assert a <= b
    assert x <= y

    mask = np.zeros(b - a, dtype=np.bool)

    # Shortcut case
    if a == x and b == y:  # Most common case?
        mask[:] = True

    if a <= b <= x <= y:
        pass  # Leave everything to false
    elif x <= y <= a <= b:
        pass  # Leave everything to false
    elif x <= a <= b <= y:  # If (a,b) in (x,y)
        mask[:] = True  # Leave everything false
    elif a <= x <= y <= b:  # If (x,y) in (a,b)
        mask[x - a:y - a] = True
    elif a <= x <= b <= y:
        mask[x - a:b - a] = True
    elif x <= a <= y <= b:
        mask[0:y - a] = True
    else:
        raise ValueError()

    return mask


def sizeof_fmt(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')
