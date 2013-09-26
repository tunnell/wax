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
"""Interface to Celery

This is the interface to celery.  You must first have done:

  celery worker --app=tasks


"""

import sys

import os
import numpy as np

from celery import Celery

sys.path.append(os.path.dirname(os.path.basename(__file__)))

from cito.helpers import combine_blocks
from cito.helpers import xedb
#from cito.helpers import sample_operations
from pint import UnitRegistry

conn, mongo_db_obj, collection = xedb.get_mongo_db_objects()

celery = Celery('tasks',
                broker='mongodb://%s:%d/celery' % (conn.host,
                                                   conn.port))

@celery.task
def flush(t0, t1):
    subset_query = {"triggertime": {'$gte': t0,
                                    '$lt': t1}}
    collection.remove(subset_query)

@celery.task
def process(t0, t1):
    """Function for processing data within Celery

    Args:
        t0 (int):  Start time in units of 10 ns
        t1 (int):  End time in units of 10 ns

    Returns:
        None
    """


    ureg = UnitRegistry()
    ureg.define("sample = 10 ns")
    ureg.define("sigwidth = 1 microsecond")

    n_samples = t1 - t0
    print('nsamples', n_samples)

    # $gte and $lt are special mongo functions for greater than and less than
    subset_query = {"triggertime": {'$gte': t0,
                                    '$lt': t1}}
    cursor = collection.find(subset_query, )
    count = cursor.count()
    print('count', count)
    if count == 0:
        return
    #t0.to('s')
    #t1.to('s')
    #if count:
    #    print('\tRange:', t0, t1, 'with %d docs' % count)
        #cursor = collection.find(subset_query,
    #                         fields=['triggertime', 'module'])

    #print('get_sum_waveform')
    results = combine_blocks.get_sum_waveform(cursor, t0,
                                              n_samples)
    y = results['occurences']


    print('shrink')
    #y = sample_operations.shrink(y, int(ureg['sigwidth'].to('sample').magnitude))


    print('fft')

    #import pyfftw

    #z = pyfftw.interfaces.numpy_fft.rfft(y, threads=8)
    z = np.fft.fft(y)
    print('fftw', z)
    res = {}
    res['t0'] = t0
    res['t1'] = t1
    res['fft'] = z
    #db.post_result(res)
    import pickle
    pickle.dump( z, open( "save.p", "wb" ) )

    # FFT convolve?
    #wavelet = ricker

    # CWT https://github.com/scipy/scipy/blob/v0.12.0/scipy/signal/wavelets.py#L314
    #output = np.zeros(len(data))
    #wavelet_data = wavelet(min(10 * width, len(data)), width)
    #output = convolve(data, wavelet_data,
    #                  mode='same')

    #print(np.fft.fft(y))
    #peaks = combine_blocks.find_peak(results['occurences'])
    #print('occurences', results['occurences'])

    if results['size'] == 0:
        return 0

    print('filter_samples')
    #y = sample_operations.filter_samples(results['occurences'])

    print('find_peaks')
    y = combine_blocks.find_peaks(y)

    print('peaks', y)

    #func(collection, cursor)

    #collection.remove(subset_query)
    return results['size']
