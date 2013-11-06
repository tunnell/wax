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
"""Speed tester

SciPyFFTWaveform is really freaking slow compared to others.  Same with FFTW.
"""

__author__ = 'tunnell'
import logging
import time

import numpy as np
import scipy
import pymongo
from cliff.command import Command

#from cito.helpers import cInterfaceV1724
from cito.helpers import xedb, waveform
from cito.base import CitoSingleCommand, TimingTask

class Fetch(TimingTask):
    """Fetch and decompress"""

    def call(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        size = 0.0
        for doc in cursor:
            size += len(xedb.get_data_from_doc(doc))
        return size


class PySumWaveform(TimingTask):
    """
    'PySumWaveform' min run time was 0.635332584 sec
'PySumWaveform' max run time was 0.650459766 sec
'PySumWaveform' avg run time was 0.644438839 sec in 10 runs
'PySumWaveform' size 1 MB 10 runs
'PySumWaveform' avg speed 1.887291191 MB/s in 10 runs
    """

    def call(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        return results['size']


class NumpyFFTWaveform(TimingTask):
    def call(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        y = results['occurences']
        np.fft.fft(y)
        return results['size']


class NumpyRealFFTWaveform(TimingTask):
    """Use Numpy for Real FFT of sum waveform

    Normal Numpy FFT is 25% slower.  SciPyFFTWaveform seems to be more than a
    factor of two slower.  PyFFTW is significantly worse than that.
    """

    def call(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        y = results['occurences']
        np.fft.rfft(y)
        return results['size']


class SciPyFFTWaveform(TimingTask):
    def call(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        y = results['occurences']
        scipy.fftpack.fft(y)
        return results['size']


class SciPyFindWaveformPeaks(TimingTask):
    def call(self, t0, t1):
        cursor = self.get_cursor(t0, t1)
        results = waveform.get_sum_waveform(cursor, t0,
                                            t1 - t0)
        y = results['occurences']
        peakind = waveform.signal.find_peaks_cwt(y, np.array([100]))
        threshold = 10000
        peaks = []

        for a, b in zip(peakind, y[peakind]):
            if b > threshold:
                peaks.append(peakind)
        peaks = np.array(peaks)

        print(peakind, peaks, y[peaks])

        return results['size']


class SpeedTestSingleCommand(CitoSingleCommand):
    """Perform a speed test
    """

    def get_tasks(self):
        tasks = [Fetch(),
                 PySumWaveform(),
                 NumpyFFTWaveform(),
                 # SciPyFindWaveformPeaks(),
                 NumpyRealFFTWaveform(),
                 SciPyFFTWaveform()
        ]

        return tasks



if __name__ == '__main__':
    x = PySumWaveform()
    x.call(0, 10 ** 8)
