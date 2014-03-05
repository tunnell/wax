import logging
import math
import time

from cliff.command import Command
from tqdm import tqdm

from cito.Database import InputDBInterface, OutputDBInterface
from cito.EventBuilder import Logic
from cito.core import Waveform
from cito.Trigger.PeakFinder import MAX_DRIFT


__author__ = 'tunnell'


class ProcessTimeBlockTask():
    """Process a time block
    """

    def __init__(self, input, output):
        self.log = logging.getLogger(__name__)

        self.input = input
        self.event_builder = Logic.EventBuilder()
        self.output = output

    def process(self, t0, t1):
        """Process a time chunk

        .. todo:: Must this know padding?  Maybe just hand cursor so can mock?

        :param t0: Initial time to query.
        :type t0: int.
        :param t1: Final time.
        :type t1: int.
        :returns:  int -- number of bytes processed
        :raises: AssertionError
        """
        data_docs = self.input.get_data_docs(t0, t1)
        data, size = Waveform.get_data_and_sum_waveform(data_docs, self.input)

        # If no data analyzed, return
        self.log.debug("Size of data analyzed: %d", size)
        if size == 0:
            self.log.debug('No data found in [%d, %d]' % (t0, t1))
            return 0

        # Build events (t0 and t1 used only for sanity checks)
        try:
            events = self.event_builder.build_event(data, t0, t1)

            if len(events):
                self.output.write_events(events)
            else:
                self.log.debug("No events found between %d and %d." % (t0, t1))

        except:
            logging.exception('Event building failed.')

        return size


class ProcessCommand(Command):
    """ProcessCommand
    """

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(ProcessCommand, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        parser.add_argument('--chunksize', type=int,
                            help="Size of data chunks to process [10 ns step]",
                            default=2 ** 26)
        parser.add_argument('--padding', type=int,
                            help='Padding to overlap processing windows [10 ns step]',
                            default=MAX_DRIFT)
        parser.add_argument('--chunks', type=int,
                            help='Numbers of chunks to analyze',
                            default=-1)

        return parser


    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)

        chunk_size = parsed_args.chunksize
        #padding = parsed_args.padding

        self.log.debug('Command line arguments: %s', str(parsed_args))

        input = InputDBInterface.MongoDBInput(hostname=parsed_args.hostname)
        output = OutputDBInterface.MongoDBOutput(collection_name=input.get_collection_name(),
                                                 hostname=parsed_args.hostname)

        task = ProcessTimeBlockTask(input, output)

        start_time = time.time()
        amount_data_processed = 0

        min_time = input.get_min_time()
        max_time = input.get_max_time()

        min_time_index = int(min_time / chunk_size)
        max_time_index = math.ceil(max_time / chunk_size) # For continous streaming, change ceil -> int

        self.log.debug("Current max time [10 ns]: %d", max_time)
        self.log.debug("Current max time [1 s]: %d", (max_time / 1e8))
        self.log.debug("Size of data blocks [10 ns]: %d" % chunk_size)
        self.log.debug("Size of data blocks [1 s]: %d" % (chunk_size / 1e8))

        for i in tqdm(range(min_time_index, max_time_index)):
            t0 = (i * chunk_size)
            t1 = (i + 1) * chunk_size

            self.log.debug('Processing %d %d' % (t0, t1))

            amount_data_processed += task.process(t0, t1)

            dt = (time.time() - start_time)
            data_rate = amount_data_processed / dt / 1000
            self.log.debug("%d bytes processed in %d seconds" % (amount_data_processed,
                                                                 dt))
            self.log.info("Rate [kBps]: %f" % (data_rate / dt))

            if parsed_args.chunks > 0 and i > parsed_args.chunks:
                break

        self.log.info("Final stats:")
        self.log.info("\t%d bytes processed in %d seconds" % (amount_data_processed,
                                                              dt))
        self.log.info("\tRate [kBps]: %f" % (amount_data_processed / dt / 1000))