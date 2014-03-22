import logging
import math
import time

from cliff.command import Command
from tqdm import tqdm

from cito.Database import InputDBInterface, OutputDBInterface
from cito.EventBuilder import Logic
from cito.core.math import sizeof_fmt
from cito.EventBuilder.Logic import MAX_DRIFT
import numpy as np

import _cito_compiled_helpers as cch

__author__ = 'tunnell'

CHUNK_SIZE = 2 ** 28

MAX_ADC_VALUE = 2 ** 14  # 14 bit ADC samples





class ProcessTask():

    """Process a time block
    """

    def __init__(self, dataset, hostname):

        self.log = logging.getLogger(__name__)

        # If dataset == None, finds a collection on its own
        self.delete_collection_when_done = True
        if dataset is not None:
            # We've chosen a dataset to process, probably for testing so don't
            # delete
            self.delete_collection_when_done = False

        self.input = InputDBInterface.MongoDBInput(collection_name=dataset,
                                                   hostname=hostname)
        if self.input.initialized:
            self.output = OutputDBInterface.MongoDBOutput(collection_name=self.input.get_collection_name(),
                                                          hostname=hostname)
        else:
            self.log.debug("Cannot setup output DB.")
            self.output = None

        self.event_builder = Logic.EventBuilder()

    def print_stats(self, amount_data_processed, dt):

        self.log.debug("%d bytes processed in %d seconds" % (amount_data_processed,
                                                             dt))
        if dt < 1.0:
            self.log.debug("Rate: N/A")
        else:
            data_rate = amount_data_processed / dt
            rate_string = sizeof_fmt(data_rate) + 'ps'
            self.log.debug("Rate: %s" % (rate_string))

    def process_dataset(self, chunk_size, chunks, padding):
        # Used for benchmarking
        start_time = time.time()

        amount_data_processed = 0

        waittime = 1  # s

        # int rounds down
        min_time_index = int(self.input.get_min_time() / chunk_size)
        current_time_index = min_time_index

        search_for_more_data = True

        while (search_for_more_data):
            if self.input.has_run_ended():
                # Round up
                self.log.info(
                    "Data taking has ended; processing remaining data.")
                max_time_index = math.ceil(
                    self.input.get_max_time() / chunk_size)
                search_for_more_data = False
            else:
                # Round down
                max_time_index = int(self.input.get_max_time() / chunk_size)

            if max_time_index > current_time_index:
                for i in tqdm(range(current_time_index, max_time_index)):
                    t0 = (i * chunk_size)
                    t1 = (i + 1) * chunk_size

                    self.log.debug(
                        'Processing [%f s, %f s]' % (t0 / 1e8, t1 / 1e8))

                    amount_data_processed += self.process_time_range(
                        t0, t1 + padding, padding)

                    self.print_stats(
                        amount_data_processed, time.time() - start_time)

                    if chunks > 0 and i > chunks:
                        search_for_more_data = False
                        break  # Breaks for loop, but not while.

                processed_time = (max_time_index - current_time_index)
                processed_time *= chunk_size / 1e8
                self.log.info("Processed %d seconds; searching for more data." % processed_time)
                current_time_index = max_time_index
            else:
                self.log.debug('Waiting %f seconds' % waittime)
                time.sleep(waittime)
                start_time = time.time()
                amount_data_processed = 0

        if self.delete_collection_when_done:
            self.drop_collection()

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

        size = 0
        reduction_factor = 200
        n = int(np.ceil((t1-t0)/reduction_factor))
        cch.setup(n)

        # Every data doc has a start time and end time.  These ranges are used
        # later to compute overlaps with event ranges.
        doc_ranges = np.zeros((len(data_docs), 2), dtype=np.int32)

        for i, doc in enumerate(data_docs):
            time_correction = doc['time'] - t0

            samples = self.input.get_data_from_doc(doc)

            # Record time range of these samples
            doc_ranges[i] = (time_correction/reduction_factor,
                             (time_correction + samples.size)/reduction_factor)

            cch.add_samples(samples, time_correction, reduction_factor)
            size += samples.size * 2

        #sum_data = cch.get_sum()

        self.log.debug("Size of data process in bytes: %d", size)

        # If no data analyzed, return
        self.log.debug("Size of data analyzed: %d", size)
        if size == 0:
            self.log.debug('No data found in [%d, %d]' % (t0, t1))
            return 0

        ranges = cch.build_events(10000, int(MAX_DRIFT/reduction_factor))


        #  One event has many samples, thus to mapping represented as samples -> event
        mappings = cch.overlaps(doc_ranges.flatten())
        events = []

        ranges *= reduction_factor
        ranges.resize((ranges.size/2, 2))

        reduced_data_count = 0

        last = None
        for i, mapping in enumerate(mappings):
            # Document has no event, then skip
            if mapping == -1:
                reduced_data_count += 1
                continue

            # If need to start event
            if last == None or last['cnt'] != mapping:
                if last != None:
                    events.append(last)
                self.log.debug('\tEvent %d', mapping)
                last = {}
                last['cnt'] = int(mapping)
                last['range'] = [int(ranges[mapping][0]),
                                 int(ranges[mapping][1])]
                last['docs'] = []

            last['docs'].append(data_docs[i])

        if len(events):
            self.output.write_events(events)
        else:
            self.log.debug("No events found between %d and %d." % (t0, t1))
        self.log.debug("Discarded: (%d/%d) = %0.3f%%",
                       reduced_data_count,
                       (len(data_docs) - reduced_data_count),
                       100*float(reduced_data_count)/(len(data_docs) - reduced_data_count))
        return size

    def drop_collection(self):
        self.input.get_db().drop_collection(self.input.get_collection_name())


class ProcessCommand(Command):

    """Start event builder and trigger software for continuous processing..

    Process data through the event builder and software trigger. The default
    behavior of this command is to take data from the input database, process
    it, then write events out to the output database.  (This command does not
    build files.)
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
                            default=(3 * MAX_DRIFT))
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
            except Exception as e:
                self.log.exception(e)
                self.log.fatal("Exception resulted in fatal error; quiting.")
                raise

            if parsed_args.chunks != -1:
                p.delete_collection_when_done = False

            if not p.input.initialized:
                self.log.warning("No dataset available to process; waiting one second.")
                time.sleep(1)
            else:
                p.process_dataset(chunk_size=parsed_args.chunksize,
                                  chunks=parsed_args.chunks,
                                  padding=parsed_args.padding)

            # If only a single dataset was specified, break
            if parsed_args.dataset is not None or parsed_args.chunks != -1:
                break

        cch.shutdown()
