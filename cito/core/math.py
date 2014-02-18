import logging

__author__ = 'tunnell'


def compute_event_ranges(peaks, range_around_peak=(-18000, 18000)):
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