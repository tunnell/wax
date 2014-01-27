# -*- coding: utf-8 -*-

"""
    cito.core.EventBuilding
    ~~~~~~~~~~~~~~~~~~~~~~~

    Event building converts time blocks of data (from different digitizer boards) into DAQ events.

    Event building (link jargon) occurs by taking all data from all boards recorded between a time window and, using
    some trigger logic, identifying independent events within this time window.  An EventBuilder class is defined
    that performs the following sequential operations:

    * Build sum waveform
    * Using trigger algorithm, identify peaks in time.
    * If there is no pileup (read further for pileup details), an event corresponds to a predefined time range before
      and after each peak.

    More technically, a boolean array is created for each time sample, where True corresponds to a sample being saved
    and false corresponds to an event being discarded.  These values default to false.  Two variables are defined by the
    user: t_pre and t_post.  For each peak that the triggering algorithm identifies (e.g., charge above 100 pe), the
    range [peak_i - t_pre, peak_i + t_post] is set to true  (see get_index_mask_for_trigger).  Subsequently, continuous
    blocks of 'true' are called an event.

    In other words, if two particles interact in the detector within a typical 'event window', then these two
    interactions are saved as one event.  Identifying how to break up the event is thus left for postprocessing.  For
    example, for peak_k > peak_i, if peak_i + t_post > peak_k - t_pre, these are one event.

    TODO: Store metadata that stores the time of each trigger.

"""
import logging

import numpy as np
from cito.Trigger import Threshold


def get_index_mask_for_trigger(size, peaks,
                               range_around_peak=(-500, 500)):
    """Creates 1D array where an element is true if respective sample should be
     saved.

    The array is by default 'false' and then, if within certain distance from a
    peak, an element is set to 'true'.

    Args:
        size (int):  An iterable object of documents containing Caen
                           blocks.  This can be a pymongo Cursor.
        peaks (list or int): The index or indices of the peaks
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
        raise ValueError(
            "peaks must be a list of integers (i.e., not a float)")

    # Physics
    # False means don't save, true means save
    to_save = np.zeros(size, dtype=np.bool)
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
        if start is None:
            start = place
        elif places_where_true[i] - places_where_true[i - 1] > 1:
            ranges.append((start, places_where_true[i - 1] + 1))
            start = place

    # Were we searching for the end of Trues but found end of array?
    if start is not None:
        ranges.append((start, places_where_true[-1] + 1))

    return ranges


def find_sum_in_data(data):
    """Find sum waveform in Xenon data


    :param data: Initial time to query.
    :type data: dict.
    :returns:  dict -- Sum waveform indices and samples.
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
        :returns:  dict -- Sum waveform indices and samples.
        :raises: ValueError
        """

        # Grab sum waveform
        sum_data = find_sum_in_data(data)
        self.log.debug('Sum waveform range: [%d, %d]', sum_data[
                       'indices'][0], sum_data['indices'][-1])

        # Sanity checks on sum waveform
        if t0 is not None and t1 is not None:
            self.log.debug(
                "Sanity check that sum waveform within inspection window")
            # Sum waveform must be in our inspection window
            assert t0 < sum_data['indices'][
                0] < t1, 'Incorrect Sum WF start time'
            assert t0 < sum_data['indices'][
                -1] < t1, 'Incorrect Sum WF end time'

        # Find peaks
        peak_indices = Threshold.trigger(
            sum_data['indices'], sum_data['samples'])
        peaks = sum_data['indices'][peak_indices]
        self.log.debug('Peak indices: %s', str(peaks))
        self.log.debug('Peak local indices: %s', str(peak_indices))
        self.log.info('Number of peaks: %d', len(peak_indices))
        if len(peak_indices) == 0:  # If no peaks found, return
            self.log.info("No peak found; returning")
            return []

        # Check peak in sum waveform
        self.log.debug("Sanity check that peaks are within sum waveform")
        for peak in peaks:  # Peak must be in our data range
            assert sum_data['indices'][0] < peak < sum_data['indices'][-1]

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

            to_save = {'data': {}}

            for key, value in data.items():
                (d0, d1, num_pmt) = key
                (indices, samples) = value['indices'], value['samples']

                if d1 < e0 or e1 < d0:  # If true, no overlap
                    continue

                if e0 <= d0 and d1 <= e1:  # Most common case:
                    s0 = 0
                    s1 = len(indices)
                else:  # compute overlap
                    overlap = np.intersect1d(np.arange(d0, d1), erange)
                    s0 = np.where(indices == overlap[0])[0][0]
                    s1 = np.where(indices == overlap[-1])[0][0]

                if num_pmt == 'sum':
                    self.log.debug('\t\tData (sum): [%d, %d]', d0, d1)
                else:
                    self.log.debug(
                        '\t\tData (PMT%d): [%d, %d]', num_pmt, d0, d1)

                to_save['data'][num_pmt] = {'indices': indices[s0:s1],
                                            'samples': samples[s0:s1]}

            to_save['peaks'] = peaks
            to_save['evt_num'] = evt_num
            to_save['range'] = [int(e0), int(e1)]
            events.append(to_save)

        return events
