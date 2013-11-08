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
import logging

import pymongo
from cito.base import CitoContinousCommand, TimingTask
import matplotlib.pyplot as plt

from cito.helpers import  waveform



class PlotWaveform(TimingTask):
    def plot(self, t0, t1, peak_indecies, results, save_range):
        fig = plt.figure(figsize=(7,5))
        #plt.title('Time from %d till %d' % (t0, t1))
        plt.plot(results['indecies'], results['samples'])
        plt.xlabel("Time [10 ns adc steps]")
        plt.ylabel("Sum charge [adc counts]")

        if t0 is not None and t1 is not None:
            plt.xlim((t0, t1))

        for peak_i in peak_indecies:
            peak_index = results['indecies'][peak_i]
            peak_value = results['samples'][peak_i]

            plt.vlines(peak_index, 0, peak_value, colors='r')
            plt.hlines(peak_value, peak_index - save_range, peak_index + save_range, colors='r')

        plt.savefig('peak_finding_%s_%s.eps' % (str(t0), str(t1)))
        plt.close(fig)
        #plt.show()

    def process(self, t0, t1):  # doesn't this need to know what the padding is?
        save_range = 100

        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        peak_indecies = waveform.find_peaks_in_data(results['indecies'], results['samples'])
        peaks = results['indecies'][peak_indecies]


        for peak in peaks:
            waveform.save_time_range(peak - save_range, peak + save_range)
            self.plot(peak - 5 * save_range, peak + 5 * save_range,
                      peak_indecies, results, save_range)

        self.plot(None, None, peak_indecies, results, save_range)

        return results['size']




class PlotWaveformSingleCommand(CitoContinousCommand):
    """Plot the sum waveform
    """

    def get_tasks(self):
        tasks = [PlotWaveform()]

        return tasks




if __name__ == '__main__':
    x = PlotWaveform()
    x.process(400, 10 ** 3)
