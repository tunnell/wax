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

    More technically, a boolean array is created for each time sample, where True corresponds to a sample being saved
    and false corresponds to an event being discarded.  These values default to false.  Two variables are defined by the
    user: t_pre and t_post.  For each peak that the triggering algorithm identifies (e.g., charge above 100 pe), the
    range [peak_i - t_pre, peak_i + t_post] is set to true  (see get_index_mask_for_trigger).  Subsequently, continuous
    blocks of 'true' are called an event.

    In other words, if two particles interact in the detector within a typical 'event window', then these two
    interactions are saved as one event.  Identifying how to break up the event is thus left for postprocessing.  For
    example, for peak_k > peak_i, if peak_i + t_post > peak_k - t_pre, these are one event.


"""
import logging

import numpy as np
from cito.Trigger import PeakFinder
from cito.core.math import compute_subranges, overlap_region


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
        ##
        # Step 1: Grab sum waveform:  this sum waveform will be used to identify S2 signals
        ##
        # sum0, sum1, time ranges
        sum_data = find_sum_in_data(data)

        sum0, sum1 = sum_data['indices'][0], sum_data['indices'][-1]
        self.log.debug('Sum waveform range: [%d, %d]', sum0, sum1)

        ##
        # Step 2: Identify peaks in sum waveform using a Trigger algorithm
        ##
        peak_indices, smooth_waveform = PeakFinder.trigger(sum_data['indices'], sum_data['samples'])
        peaks = sum_data['indices'][peak_indices]
        for peak in peaks:  # Check peak in sum waveform
            assert sum_data['indices'][0] < peak < sum_data['indices'][-1]
        self.log.debug('Peak indices: %s', str(peaks))
        self.log.debug('Peak local indices: %s', str(peak_indices))
        if len(peak_indices) == 0:  # If no peaks found, return
            self.log.info("No peak found; returning")
            return []
        else:
            self.log.info("Peaks found: %s" % str(peaks))

        ##
        # Step 3: Flag ranges around peaks to save, then break into events
        ##
        event_ranges = compute_subranges(peaks)
        self.log.info('%d trigger events from %d peaks', len(event_ranges), len(peak_indices))


        data[(sum0, sum1, 'smooth')] = {'indices': sum_data['indices'],
                                        'samples': smooth_waveform}

        ##
        # Step 4: For each trigger event, associate channel information
        ##
        events = []
        for e0, e1 in event_ranges:
            # e0, e1 are the times for this trigger event
            #e0 += t0
            #e1 += t0
            evt_num = self.get_event_number()
            self.log.info('\tEvent %d: [%d, %d]', evt_num, e0, e1)

            #  This information will be saved about the trigger event
            to_save = {'data': {}}

            # If there data within our search range [e0, e1]?
            for key, value in data.items():
                #if key[2] == 'sum':
                #    continue

                samples = value['samples']
                indices = value['indices']
                assert samples.size == indices.size

                # d0 is start time for this channel data, d1 therefore end time
                (d0, d1, num_pmt) = key

                if key[2] != 'sum':
                    assert len(samples) == (d1 - d0), '%d %d %d' % (samples.size, d0, d1)

                s0, s1 = overlap_region((d0, d1), (e0, e1))
                if s0 is None or s1 is None:
                    continue
                self.log.debug("%s %d %d" % (str(key), s0, s1))
                try:
                    s0 = np.where(indices == s0)[0][0]
                    s1 = np.where(indices == s1-1)[0][0]
                except IndexError:
                    self.log.error("%s %d %d" % (str(key), s0, s1))
                    self.log.error(indices)
                    raise


                if num_pmt == 'sum':
                    self.log.debug('\t\tData (sum): [%d, %d]', d0, d1)
                else:
                    self.log.debug('\t\tData (PMT%d): [%d, %d]', num_pmt, d0, d1)

                to_save['data'][num_pmt] = {'indices': indices[s0:s1],
                                            'samples': samples[s0:s1]}

            to_save['peaks'] = peaks
            #to_save['sum_data'] = {'samples': sum_data['samples'],
            #                       'indices': sum_data['indices'], }

            to_save['evt_num'] = evt_num
            to_save['smooth'] = smooth_waveform
            to_save['range'] = [int(e0), int(e1)]
            events.append(to_save)

        return events


if __name__ == '__main__':
    import sys
    from cito.core.main import CitoApp

    myapp = CitoApp()
    code = myapp.run(['process'])
    sys.exit(code)
