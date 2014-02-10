"""Tasks that can be performed on contigous time slices.

Each type of processing that can occur on sequential data is represented
as a class here.

.. todo::  t0, t1 -> range = ().  Is that clearer?

.. moduleauthor:: Christopher Tunnell <ctunnell@nikhef.nl>

"""
import logging

from cito.core import Waveform, XeDB
from cito.EventBuilder import EventBuilding


class ProcessTimeBlockTask():
    """Process a time block
    """

    def __init__(self, output):
        self.log = logging.getLogger(__name__)
        self.event_builder = EventBuilding.EventBuilder()
        self.output = output

    def process(self, t0, t1):
        """Process a time chunk

        .. todo:: Must this know padding?  Maybe just hand cursor so can mock?

        :param t0: Initial time to query.
        :type t0: int.
        :param t1: Final time.
        :type t1: int.
        :returns:  int -- number of bytes processed
        :raises: AssertionError
        """
        data_docs = XeDB.get_data_docs(t0, t1)
        data, size = Waveform.get_data_and_sum_waveform(data_docs, t1 - t0)

        # If no data analyzed, return
        self.log.debug("Size of data analyzed: %d", size)
        if size == 0:
            self.log.warning('No data found in [%d, %d]' % (t0, t1))
            return 0

        # Build events (t0 and t1 used only for sanity checks)
        try:
            events = self.event_builder.build_event(data, t0, t1)

            if len(events):
                self.output.write_events(events)
            else:
                self.log.warning("No events found between %d and %d." % (t0, t1))

        except:
            logging.exception('Event building failed.')

        return size
