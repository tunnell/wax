# -*- coding: utf-8 -*-

"""
    cito.core.EventBuilding
    ~~~~~~~~~~~~~~~~~~~~~~~

    Event building converts time blocks of data (from different digitizer boards) into DAQ events.

    Event building (see jargon) occurs by taking all the data from all the boards recorded during a time window and,
    using some trigger logic, identifying independent events within this time window.  An EventBuilder class is defined
    that performs the following sequential operations:

    * Build sum waveform
    * Using trigger algorithm, identify peaks in time.
    * If there is no pileup (read further for pileup details), an event corresponds to a predefined time range before
      and after each peak.

    More technically about pileup, if two particles interact in the detector within a typical 'event window', then
    these two interactions are saved as one event.  Identifying how to break up the event is thus left for
    postprocessing.  For example, for peak_k > peak_i, if peak_i + t_post > peak_k - t_pre, these are one event.
"""
import logging

import numpy as np

from cito.Trigger import PeakFinder
from cito.core.math import compute_subranges, find_subranges

MAX_DRIFT = 18000  # units of 10 ns

def find_sum_in_data(data):
    """Find sum waveform in channel data


    :param data: Initial time to query.
    :type data: dict.
    :returns:  dict -- Sum waveform indices and samples.
    :raises: ValueError
    """
    for key, value in data.items():
        start, stop, pmt_num = key
        if pmt_num == 'sum':
            sum0, sum1 = value['indices'][0], value['indices'][-1]
            logging.debug('Sum waveform range: [%d, %d]', sum0, sum1)
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

    def build_event(self, data_docs, event_ranges,
                    time_range, padding):
        """Build events out of raw data.

        Using the sum waveform provided as an input, distinct events are identified.
        Subsequently, all of the relevant individual channel PMT information (also
        an input) is saved for that specific event.

        :param data: Data to query, including sum waveform and individual channels
        :type data: dict.
        :param t0: Earliest possible time for sanity checks.  If None, skip check.
        :type t0: int.
        :param t1: Latest possible time for sanity checks.  If None, skip check.
        :type t1: int.
        :returns:  dict -- Sum waveform indices and samples.
        :raises: ValueError
        """
        t0, t1 = time_range


        # More docs on

        ##
        # Step 4: For each trigger event, associate channel information
        ##
        events = []
        # e0, e1 are the times for this trigger event
        for e0, e1 in event_ranges:
            #  This information will be saved about the trigger event
            to_save = {'data': []}

            # Logic to deal with overlapping region
            # if e1 > t1:
            #     if e0 < t1 - padding:
            #         self.log.error("Event bigger than overlap region.  Flagging 1 second of deadtime.")
            #         to_save['peaks'] = [peak for peak in peaks if e0 < peak < e1]
            #         to_save['evt_num'] = "deadtime"
            #         to_save['error'] = "Event range [%d, %d] greater than overlap window!" % (e0, e1)
            #         to_save['range'] = [int(e0 - 5e7), int(e1 + 5e7)]
            #         events.append(to_save)
            #     continue
            # if e0 < t0 + padding:
            #     continue

            evt_num = self.get_event_number()
            self.log.debug('\tEvent %d: [%d, %d]', evt_num, e0, e1)

            # If there data within our search range [e0, e1]?
            for doc in data_docs:
                d0 = doc['time'] - t0
                d1 = d0 + len(doc['data'])/2

                if d1 < e0 or d0 > e1:
                    continue

                to_save['data'].append(doc)

            to_save['evt_num'] = evt_num
            to_save['range'] = [int(e0), int(e1)]
            to_save['_id'] = evt_num
            events.append(to_save)

        return events


if __name__ == '__main__':
    import sys
    from cito.core.main import CitoApp

    myapp = CitoApp()
    import cProfile

    cProfile.run("""myapp.run(['process', '--chunks', '15'])""",
                 'profile')

    sys.exit(0)
