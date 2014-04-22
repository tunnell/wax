from configglue import schema

MAX_DRIFT = 18000  # units of 10 ns
HOSTNAME = '127.0.0.1'

class Mongo(schema.Section):
    hostname = schema.StringOption(default=HOSTNAME,
                                   help="MongoDB database address")
    #port = schema.IntOption(default=27017,
    #                        help='port')

class File(schema.Section):
    filename = schema.StringOption(default='cito_file.pklz',
                                           help='filename')

class EventBuilder(schema.Section):
    chunksize = schema.IntOption(default=2 ** 28,
                                  help='How many samples to search at once')

    padding = schema.IntOption(help='Padding to overlap processing windows [10 ns step]',
                            default=(3 * MAX_DRIFT))

    chunks = schema.IntOption(help='Limit the numbers of chunks to analyze (-1 means no limit)',
                              default=-1)

    dataset = schema.StringOption(help='Analyze only a single dataset',
                                  default=None)


