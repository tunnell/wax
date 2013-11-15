# cito - The Xenon1T experiments software trigger
# Copyright 2013.  All rights reserved.
# https://github.com/tunnell/cito
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of the Xenon experiment, nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Plot waveform

Make a plot of the sum waveform for a time range.
"""

__author__ = 'tunnell'

from cito.base import CitoContinousCommand, TimingTask


from cito.helpers import  waveform
from cito.helpers import Output


class PlotWaveform(TimingTask):
    def __init__(self):
        TimingTask.__init__(self)
        self.e = Output.EpsOutput()

    @staticmethod
    def find_sum_in_data(data):
        for key, value in data.items():
            start, stop, pmt_num = key
            if pmt_num == 'sum':
                return value
        raise ValueError("Sum waveform not found")

    def process(self, t0, t1):  # doesn't this need to know what the padding is?
        save_range = 500 # How much data to save around peak

        cursor = self.get_cursor(t0, t1)
        data, size = waveform.get_data_and_sum_waveform(cursor, t1 - t0)

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
        peak_indecies = waveform.find_peaks_in_data(sum_data['indecies'], sum_data['samples'])
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

        # Save peaks
        self.e.write_data_range(t0, t1, data, peaks, save_range)

        return size




class PlotWaveformSingleCommand(CitoContinousCommand):
    """Plot the sum waveform
    """



    def get_tasks(self):

        tasks = [PlotWaveform()]
        self.log.debug('Getting tasks: %s', str(tasks))
        return tasks




if __name__ == '__main__':
    x = PlotWaveform()
    x.process(400, 10 ** 3)
