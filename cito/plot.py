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


from cito.helpers import  waveform



class PlotWaveform(TimingTask):
    """
    'PySumWaveform' min run time was 0.635332584 sec
'PySumWaveform' max run time was 0.650459766 sec
'PySumWaveform' avg run time was 0.644438839 sec in 10 runs
'PySumWaveform' size 1 MB 10 runs
'PySumWaveform' avg speed 1.887291191 MB/s in 10 runs
    """

    def process(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)

        import matplotlib.pyplot as plt
        plt.figure()
        plt.title('Time from %d till %d' % (t0, t1))
        plt.plot(results['occurences'])
        #plt.xlim((t0, t1))
        plt.show()
        print(results)
        raw_input()
        raise ValueError()
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
