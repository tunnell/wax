# -*- coding: utf-8 -*-

"""
    cito.core.EventBuilding
    ~~~~~~~~~~~~~~~~~~~~~~~

    Say something here.

    Say more here.

"""
import logging

import numpy as np

from cito.core import Waveform


def get_index_mask_for_trigger(size, peaks,
                               range_around_peak=(-500, 500)):
    """Creates 1D array where an element is true if respective sample should be
     saved.

    The array is by default 'false' and then, if within certain distance from a
    peak, an element is set to 'true'.

    Args:
        size (int):  An iterable object of documents containing Caen
                           blocks.  This can be a pymongo Cursor.
        peaks (list or int): The index or indecies of the peaks
        range_around_trigger (tuple): The range around the peak to save.  Note that there
                                      is no wrap around.

    Returns:
       np.ndarray(dtype=np.bool):  Boolean array of length size which says whether or not
                                    to save a certain index.

    """
    # Bureaucracy
    log = logging.getLogger('waveform')
    if not isinstance(size, int):
        raise ValueError('Size must be int')
    if isinstance(peaks, int):
        peaks = [peaks]
    elif isinstance(peaks, float):
        raise ValueError("peaks must be a list of integers (i.e., not a float)")

    # Physics
    to_save = np.zeros(size, dtype=np.bool)  # False means don't save, true means save
    for peak in peaks:  # For each triggered peak
        # The 'min' and 'max' are used to prevent wrap around
        this_range = np.arange(max(peak + range_around_peak[0], 0),
                               min(peak + range_around_peak[1], size))

        #  'True' is set for every index in 'this_range'
        to_save[this_range] = True

    log.debug('Save range: %s', str(to_save))
    return to_save


def split_boolean_array(bool_array):
    """For boolean arrays, something similar to Python native string split()

    Will return the boundaries of contingous True ranges.

    Args:
        bool_array (np.array(dtype=np.bool)):  Boolean array to search

    Returns:
       list: A 2tuple of boundaries for True ranges

    """

    ranges = []

    places_where_true = np.flatnonzero(bool_array)

    start = None
    for i, place in enumerate(places_where_true):
        if start == None:
            start = place
        elif places_where_true[i] - places_where_true[i - 1] > 1:
            ranges.append((start, places_where_true[i - 1] + 1))
            start = place

    # Were we searching for the end of Trues but found end of array?
    if start != None:
        ranges.append((start, places_where_true[-1] + 1))

    return ranges


def find_sum_in_data(data):
    """Find sum waveform in Xenon data


    :param data: Initial time to query.
    :type data: dict.
    :returns:  dict -- Sum waveform indecies and samples.
    :raises: ValueError
    """
    for key, value in data.items():
        start, stop, pmt_num = key
        if pmt_num == 'sum':
            return value
    raise ValueError("Sum waveform not found")


class EventBuilder():
    """From data, construct events

    This is a separate class since it has to keep track of event number"""

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.event_number = None

    def get_event_number(self):
        if self.event_number is None:
            self.event_number = 0
            return self.event_number
        else:
            self.event_number += 1
            return self.event_number

    def build_event(self, data, t0=None, t1=None):
        """Build events out of raw data.

        Identify peaks, select events, and return event ranges.

        :param data: Data to query, including sum waveform
        :type data: dict.
        :param t0: Earliest possible time for sanity checks.  If None, skip check.
        :type t0: int.
        :param t1: Latest possible time for sanity checks.  If None, skip check.
        :type t1: int.
        :returns:  dict -- Sum waveform indecies and samples.
        :raises: ValueError
        """


        # Grab sum waveform
        sum_data = find_sum_in_data(data)
        self.log.debug('Sum waveform range: [%d, %d]', sum_data['indecies'][0], sum_data['indecies'][-1])

        # Sanity checks on sum waveform
        if t0 is not None and t1 is not None:
            self.log.debug("Sanity check that sum waveform within inspection window")
            # Sum waveform must be in our inspection window
            assert t0 < sum_data['indecies'][0] < t1, 'Incorrect Sum WF start time'
            assert t0 < sum_data['indecies'][-1] < t1, 'Incorrect Sum WF end time'

        # Find peaks
        peak_indecies = Waveform.find_peaks_in_data(sum_data['indecies'], sum_data['samples'])
        peaks = sum_data['indecies'][peak_indecies]
        self.log.debug('Peak indecies: %s', str(peaks))
        self.log.debug('Peak local indecies: %s', str(peak_indecies))
        self.log.info('Number of peaks: %d', len(peak_indecies))
        if len(peak_indecies) == 0: # If no peaks found, return
            self.log.info("No peak found; returning")
            return 0

        # Check peak in sum waveform
        self.log.debug("Sanity check that peaks are within sum waveform")
        for peak in peaks:  # Peak must be in our data range
            assert sum_data['indecies'][0] < peak < sum_data['indecies'][-1]


        # Flag samples to save
        to_save_bool_mask = get_index_mask_for_trigger(t1 - t0, peaks - t0)

        # Find time ranges corresponding to contigous samples to save
        event_ranges = split_boolean_array(to_save_bool_mask)

        events = []
        for e0, e1 in event_ranges:
            e0 += t0
            e1 += t0

            evt_num = self.get_event_number()
            self.log.info('\tEvent %d: [%d, %d]', evt_num, e0, e1)

            erange = np.arange(e0, e1)

            to_save = {'data' : {}}

            for key, value in data.items():
                (d0, d1, num_pmt) = key
                (indecies, samples) = value['indecies'], value['samples']

                if d1 < e0 or e1 < d0: # If true, no overlap
                    continue

                if e0 <= d0 and d1 <= e1:  # Most common case:
                    s0 = 0
                    s1 = len(indecies)
                else:  # compute overlap
                    overlap = np.intersect1d(np.arange(d0, d1), erange)
                    s0 = np.where(indecies == overlap[0])[0][0]
                    s1 = np.where(indecies == overlap[-1])[0][0]

                if num_pmt == 'sum':
                    self.log.debug('\t\tData (sum): [%d, %d]', d0, d1)
                else:
                    self.log.debug('\t\tData (PMT%d): [%d, %d]', num_pmt, d0, d1)

                to_save['data'][num_pmt] = {'indecies': indecies[s0:s1],
                                    'samples': samples[s0:s1]}

            to_save['peaks'] = peaks
            to_save['evt_num'] = evt_num
            to_save['range'] = [int(e0), int(e1)]
            events.append(to_save)

        return events


