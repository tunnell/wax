"""Interface to Caen V1724

Flash ADC board.  There are many Cython wrappers, which means that the code
can be compiled.
"""

import numpy as np

# Samples are actually 14 bit unsigned, so 16 bit signed fine
SAMPLE_TYPE = np.int16
MAX_ADC_VALUE = 2 ** 14   # 14 bit ADC samples
SAMPLE_TIME_STEP = 1    # 10 ns

N_CHANNELS_IN_DIGITIZER = 8  # number of channels in digitizer board


def get_samples(data):
    # Parse data
    if len(data) > 32000:
        raise ValueError('Data from board larger than memory on board')

    samples = np.frombuffer(data, dtype=np.int16)

    if np.max(samples) >= MAX_ADC_VALUE or np.min(samples) < 0:
        raise ValueError('Corrupt data since more than 14 bits used')

    # Sanity check
    #for i in range(len(data)):
    #    # the 32nd, 31st, 15th, and 16th bits should be zero
    #    assert (int(data[i]) & 0x0C000C000) == 0, "Sample format incorrect"

    # Invert pulse so larger energy deposit is larger ADC values
    samples *= -1
    samples += MAX_ADC_VALUE

    return samples
