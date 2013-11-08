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



class PlotWaveform(TimingTask):


    def process(self, t0, t1):  # doesn't this need to know what the padding is?
        save_range = 100

        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        peak_indecies = waveform.find_peaks_in_data(results['indecies'], results['samples'])
        peaks = results['indecies'][peak_indecies]

        #for peak in peaks:
        #    self.plot(peak - 5 * save_range, peak + 5 * save_range,
        #              peak_indecies, results, save_range)
        #self.plot(None, None, peak_indecies, results, save_range)

        #waveform.get_index_mask_for_trigger(t1 - t0, peaks, range_around_trigger=(-1*save_range, save_range))
        all_data = results['all_data']
        import pickle
        f = open( "save.p", "wb" )
        print(all_data)
        pickle.dump(t0,f )
        pickle.dump(t1,f )
        pickle.dump(peaks,f)
        pickle.dump( all_data, f)
        f.close()
        raise ValueError
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
