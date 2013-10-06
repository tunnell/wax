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
"""Interface to Caen V1724 through Swig.

Flash ADC board.
"""
import numpy as np
from cito.helpers import CaenBlockParsing


def get_waveform(data, n):
    a = np.fromstring(data, dtype='uint32')
    CaenBlockParsing.setup_return_buffer(n)

    assert (len(data) != 0)
    CaenBlockParsing.inplace(a)
    #CaenBlockParsing.put_samples_into_occurences
    results = []
    for i in range(8):
        samples = np.zeros(n, dtype='int32')
        indecies = np.zeros(n, dtype='uint32')

        length = CaenBlockParsing.get_data(samples, indecies, i)

        if length > 0:
            samples = np.compress(length * [True], samples)
            indecies = np.compress(length * [True], indecies)

            samples -= 2 ** 14
            samples *= -1

        else:
            samples = np.array([], dtype=np.uint32)
            indecies = np.array([], dtype=np.uint32)

        results.append((samples, indecies))
    return results
