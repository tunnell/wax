from configglue import schema
import numpy as np

MAX_ADC_VALUE = 2 ** 14  # 14 bit ADC samples
MAX_DRIFT = 18000  # units of 10 ns
HOSTNAME = '127.0.0.1'

CHUNKSIZE = 2 ** 28
PADDING = (5 * MAX_DRIFT)
# Samples are actually 14 bit unsigned, so 16 bit signed fine
SAMPLE_TYPE = np.int16

# 1 ADC count = 2.2 V / 2^14
# 10 ns samples
# 2.4 mV * us = 150 pe   ->  0.2 V 10 ns
THRESHOLD = 10000 # ADC counts, 10 ADC counts / pe

class Mongo(schema.Section):
    hostname = schema.StringOption(default=HOSTNAME,
                                   help="MongoDB database address")
    # port = schema.IntOption(default=27017,
    #                        help='port')


class File(schema.Section):
    filename = schema.StringOption(default='cito_file.pklz',
                                           help='filename')


class EventBuilder(schema.Section):
    chunksize = schema.IntOption(default=CHUNKSIZE,
                                 help='How many samples to search at once')

    padding = schema.IntOption(help='Padding to overlap processing windows [10 ns step]',
                               default=PADDING)

    chunks = schema.IntOption(help='Limit the numbers of chunks to analyze (-1 means no limit)',
                              default=-1)

    threshold = schema.IntOption(help='Threshold [adc counts]',
                                 default=THRESHOLD)

    dataset = schema.StringOption(help='Analyze only a single dataset',
                                  default=None)

    profile = schema.BoolOption(help='run profiler', default=False)
    celery = schema.BoolOption(help='use celery for parallelism', default=False)