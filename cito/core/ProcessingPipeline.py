__author__ = 'tunnell'

from cito.core import Waveform
from cito.core import Output

from cito.base import TimingTask  # Still want this?


class ProcessTimeBlockTask(TimingTask):
    def __init__(self):
        TimingTask.__init__(self)
        self.e = Output.EpsOutput()

        # TODO: config file?
        self.save_range = 500 # How much data to save around peak

        # Function for getting data
        self.f_get = Waveform.get_data_and_sum_waveform


    @staticmethod
    def find_sum_in_data(data):
        for key, value in data.items():
            start, stop, pmt_num = key
            if pmt_num == 'sum':
                return value
        raise ValueError("Sum waveform not found")

    def process(self, t0, t1):  # doesn't this need to know what the padding is?
        cursor = self.get_cursor(t0, t1)
        data, size = self.f_get(cursor, t1 - t0)

        # If no data analyzed, return
        self.log.debug("Size of data analyzed: %d", size)
        if size == 0:
            return 0

        sum_data = self.find_sum_in_data(data)

        # Sanity checks on sum waveform
        self.log.debug("Sanity check that sum waveform within inspection window")
        assert t0 < sum_data['indecies'][0] < t1, sum_data['indecies'][0]   # Sum waveform must be in our inspection window
        assert t0 < sum_data['indecies'][1] < t1, sum_data['indecies'][1]   # ditto as above line

        # Get peaks, return if none
        self.log.debug('Sum waveform range: [%d, %d]', sum_data['indecies'][0], sum_data['indecies'][-1])
        peak_indecies = Waveform.find_peaks_in_data(sum_data['indecies'], sum_data['samples'])
        peaks = sum_data['indecies'][peak_indecies]
        self.log.info('Number of peaks: %d', len(peak_indecies))
        if len(peak_indecies) == 0: # If no peaks found, return
            pass#    return 0
        self.log.debug('Peak indecies: %s', str(peaks))

        self.log.debug('Peak local indecies: %s', str(peak_indecies))

        # Some sanity checks
        self.log.debug("Sanity check that peaks are within sum waveform")
        for peak in peaks:  # Peak must be in our data range
            assert sum_data['indecies'][0] < peak < sum_data['indecies'][-1]

        to_save_bool_mask = Waveform.get_index_mask_for_trigger(t1 - t0, peaks - t0,
                                                                range_around_trigger=(-1*save_range,
                                                                                        save_range))
        event_ranges = Waveform.split_boolean_array(to_save_bool_mask)

        # Save peaks
        self.e.write_data_range(t0, t1, data, peaks, event_ranges)

        return size

