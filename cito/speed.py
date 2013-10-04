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
#import pyfftw
import scipy
import pymongo

from cito.helpers import cInterfaceV1724
from cliff.command import Command

from cito.helpers import xedb, waveform


class TimingTask():

    def process(self, t0, t1, loops=1, verbose=False):
        sums = 0.0
        mins = 1.7976931348623157e+308
        maxs = 0.0
        print('====%s Timing====' % self.__class__.__name__)
        for i in range(0, loops):
            start_time = time.time()
            result = self.call(t0, t1)
            dt = time.time() - start_time
            mins = dt if dt < mins else mins
            maxs = dt if dt > maxs else maxs
            sums += dt
            if verbose == True:
                print('\t%r ran in %2.9f sec on run %s' %
                      (self.__class__.__name__, dt, i))
        print('%r min run time was %2.9f sec' %
              (self.__class__.__name__, mins))
        print('%r max run time was %2.9f sec' %
              (self.__class__.__name__, maxs))
        print('%r avg run time was %2.9f sec in %s runs' %
              (self.__class__.__name__, sums / loops, loops))

        size = result / 1024 / 1024  # MB
        print('%r size %d MB %s runs' % (self.__class__.__name__, size, loops))
        speed = size / (sums / loops)
        print('%r avg speed %2.9f MB/s in %s runs' %
              (self.__class__.__name__, speed, loops))
        print('==== end ====')
        return result

    def get_cursor(self, t0, t1):
        conn, mongo_db_obj, collection = xedb.get_mongo_db_objects()

        # $gte and $lt are special mongo functions for greater than and less than
        subset_query = {"triggertime": {'$gte': t0,
                                        '$lt': t1}}
        return collection.find(subset_query)

    def call(self, t0, t1):
        raise NotImplementedError()


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

# class FFTWWaveform(TimingTask):
#    def call(self, t0, t1):
#        cursor = self.get_cursor(t0, t1)
#        results = waveform.get_sum_waveform(cursor, t0,
#                                              t1 - t0)
#        y = results['occurences']
#        pyfftw.interfaces.numpy_fft.rfft(y, threads=1)
#        return results['size']


class SpeedTest(Command):

    """Process data from DB online
    """

    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(SpeedTest, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        parser.add_argument('--chunksize', type=int,
                            help="Size of data chunks to process [10 ns step]",
                            default=2 ** 17)
        parser.add_argument('--padding', type=int,
                            help='Padding to overlap processing windows [10 ns step]',
                            default=10 ** 2)

        return parser

    def get_tasks(self):
        tasks = [Fetch(),
                 PySumWaveform(),
                 # NumpyFFTWaveform(),
                 # SciPyFindWaveformPeaks(),
                 # FFTWWaveform(),
                 NumpyRealFFTWaveform(),
                 # SciPyFFTWaveform()
                 ]

        return tasks

    def take_action(self, parsed_args):
        chunk_size = parsed_args.chunksize
        padding = parsed_args.padding

        conn, my_db, collection = xedb.get_mongo_db_objects(
            parsed_args.hostname)

        # Key to sort by so we can use an index for quick query
        sort_key = [
            ('triggertime', pymongo.DESCENDING),
            ('module', pymongo.DESCENDING)
        ]

        # Index for quick query
        collection.create_index(sort_key, dropDups=True)
        t0 = xedb.get_min_time(collection)

        t1 = t0 + chunk_size

        self.log.info('Processing %d %d' % (t0, t1))

        for task in self.get_tasks():
            print(task.process(t0, t1, loops=10))


if __name__ == '__main__':
    """User for profiling"""
    task = PySumWaveform()
    task.call(5702, 1000005702)