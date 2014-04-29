from configglue import schema
import numpy as np

MAX_ADC_VALUE = 2 ** 14  # 14 bit ADC samples
MAX_DRIFT = 18000  # units of 10 ns
HOSTNAME = '127.0.0.1'
CHUNK_SIZE = 2 ** 28
PADDING = (3 * MAX_DRIFT)
# Samples are actually 14 bit unsigned, so 16 bit signed fine
SAMPLE_TYPE = np.int16

class Mongo(schema.Section):
    hostname = schema.StringOption(default=HOSTNAME,
                                   help="MongoDB database address")
    #port = schema.IntOption(default=27017,
    #                        help='port')

class File(schema.Section):
    filename = schema.StringOption(default='cito_file.pklz',
                                           help='filename')

class EventBuilder(schema.Section):
    chunksize = schema.IntOption(default=CHUNK_SIZE,
                                  help='How many samples to search at once')

    padding = schema.IntOption(help='Padding to overlap processing windows [10 ns step]',
                            default=PADDING)

    chunks = schema.IntOption(help='Limit the numbers of chunks to analyze (-1 means no limit)',
                              default=-1)

    dataset = schema.StringOption(help='Analyze only a single dataset',
                                  default=None)


