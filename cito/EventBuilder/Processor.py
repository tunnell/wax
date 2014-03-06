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

CHUNK_SIZE = 2**26
class ProcessTask():
    """Process a time block
    """

    def __init__(self, dataset, hostname):

        self.log = logging.getLogger(__name__)

        # If dataset == None, finds a collection on its own
        self.input = InputDBInterface.MongoDBInput(collection_name=dataset,
                                              hostname=hostname)
        self.output = OutputDBInterface.MongoDBOutput(collection_name=self.input.get_collection_name(),
                                                 hostname=hostname)

        self.event_builder = Logic.EventBuilder()

    def process_dataset(self, chunk_size, chunks, padding):
        # Used for benchmarking
        start_time = time.time()
        amount_data_processed = 0

        waittime = 1 # s

        # int rounds down
        min_time_index = int(self.input.get_min_time() / chunk_size)
        current_time_index = min_time_index

        search_for_more_data = True

        # Loop until Ctrl-C or error
        while (search_for_more_data):
            self.log.debug("Entering while loop; use Ctrl-C to exit")

            try:
                if self.input.has_run_ended():
                    # Round up
                    self.log.debug("Run has ended")
                    max_time_index = math.ceil(self.input.get_max_time() / chunk_size)
                    search_for_more_data = False
                else:
                    # Round down
                    max_time_index = int(self.input.get_max_time() / chunk_size)

                if max_time_index > current_time_index:
                    for i in tqdm(range(min_time_index, max_time_index)):
                        t0 = (i * chunk_size)
                        t1 = (i + 1) * chunk_size

                        self.log.debug('Processing [%f s, %f s]' % (t0/1e8, t1/1e8))

                        amount_data_processed += self.process_time_range(t0, t1 + padding, padding)

                        dt = (time.time() - start_time)
                        data_rate = amount_data_processed / dt / 1000
                        self.log.debug("%d bytes processed in %d seconds" % (amount_data_processed,
                                                                             dt))
                        self.log.info("Rate [kBps]: %f" % (data_rate))

                        if chunks > 0 and i > chunks:
                            search_for_more_data = False
                            break
                    current_time_index = max_time_index
                else:
                    self.log.debug('Waiting %f seconds' % waittime)
                    time.sleep(waittime)
            except KeyboardInterrupt:
                self.log.info("Ctrl-C caught so exiting.")
                return

        self.drop_collection()
        self.log.info("Stats:")
        self.log.info("\t%d bytes processed in %d seconds" % (amount_data_processed,
                                                              dt))
        self.log.info("\tRate [kBps]: %f" % (amount_data_processed / dt / 1000))


    def process_time_range(self, t0, t1, padding):
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
            events = self.event_builder.build_event(data, t0, t1, padding)

            if len(events):
                self.output.write_events(events)
            else:
                self.log.debug("No events found between %d and %d." % (t0, t1))

        except:
            logging.exception('Event building failed.')

        return size

    def drop_collection(self):
        self.input.get_db().drop_collection(self.input.get_collection_name())



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
                            default=CHUNK_SIZE)
        parser.add_argument('--padding', type=int,
                            help='Padding to overlap processing windows [10 ns step]',
                            default=(3*MAX_DRIFT))
        parser.add_argument('--chunks', type=int,
                            help='Limit the numbers of chunks to analyze (-1 means no limit)',
                            default=-1)

        parser.add_argument('--dataset', type=str,
                            help='Analyze only a single dataset')

        return parser




    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)

        self.log.debug('Command line arguments: %s', str(parsed_args))

        while True:
            try:
                p = ProcessTask(parsed_args.dataset, parsed_args.hostname)
            except RuntimeError:
                self.log.error("No dataset found; waiting")
                time.sleep(1)
                continue

            p.process_dataset(chunk_size = parsed_args.chunksize,
                              chunks = parsed_args.chunks,
                              padding = parsed_args.padding)

            # If only a single dataset was specified, break
            if parsed_args.dataset is not None:
                break