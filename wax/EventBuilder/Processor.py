"""Processing class for the event builder (incl. software trigger)
"""

import math
import logging
import time

import numpy as np

import snappy
import _wax_compiled_helpers as cch
from tqdm import tqdm
from wax.Configuration import SAMPLE_TYPE, MAX_DRIFT
from wax.Database import InputDBInterface, OutputDBInterface
from wax import Configuration


__author__ = 'tunnell'


def get_samples_from_doc(doc, is_compressed):
    """From a mongo document, fetch the data payload and decompress if
    necessary

    Args:
       doc (dictionary):  Document from mongodb to analyze

    Returns:
       bytes: decompressed data

    """
    data = doc['data']
    assert len(data) != 0

    if is_compressed:
        data = snappy.uncompress(data)

    data = np.fromstring(data,
                         dtype=SAMPLE_TYPE)
    if len(data) == 0:
        raise IndexError("Data has zero length")

    return data


def sizeof_fmt(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')

def sampletime_fmt(num):
    num *= 10
    for x in ['ns', 'us', 'ms']:
        if num < 1000.0:
            return "%3.1f %s" % (num, x)
        num /= 1000.0
    return "%3.1f %s" % (num, 's')



class ProcessTask():
    """Process a time block
    """


    def __init__(self, chunk_size=Configuration.CHUNK_SIZE,
                 padding=Configuration.PADDING):
        """None dataset means it will find it

        """

        self.log = logging.getLogger(__name__)
        self._input = None
        self._output = None

        if chunk_size <= 0:
            raise ValueError("chunk_size <= 0: cannot analyze negative number of samples.")
        self.log.error("using chunk size of %s" % sampletime_fmt(chunk_size))
        self.chunk_size = chunk_size

        if padding < 0:
            raise ValueError("padding < 0: cannot analyze negative number of samples.")
        if padding >= chunk_size:
            self.warning("Padding is bigger than chunk?")
        self.log.error("using padding of %s" % sampletime_fmt(padding))
        self.padding = padding


    def _initialize(self, dataset=None, hostname='127.0.0.1'):
        """If dataset == None, finds a collection on its own"""
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


    def process_single_dataset(self, hostname, dataset):
        #def EventBuilderDatasetLooper(hostname, dataset, chunks, chunksize, padding):
        """This function makes lots of processing classes"""

        try:
            self._initialize(dataset=dataset,
                             hostname=hostname)
        except Exception as e:
            self.log.exception(e)
            self.log.fatal("Exception resulted in fatal error; quiting.")
            raise

        if not self.input.initialized:
            self.log.fatal("No dataset available to process; exiting.")
            return
        else:
            self._process_chosen_dataset()



    def loop_and_find_new_datasets(self, hostname):
        #def EventBuilderDatasetLooper(hostname, dataset, chunks, chunksize, padding):
        """This function makes lots of processing classes"""
        while True:
            try:
                self._initialize(hostname=hostname) # Dataset=None means it finds one
            except Exception as e:
                self.log.exception(e)
                self.log.fatal("Exception resulted in fatal error; quiting.")
                raise

            if not self.input.initialized:
                self.log.warning("No dataset available to process; waiting one second.")
                time.sleep(1)
            else:
                self._process_chosen_dataset()



    def _print_stats(self, amount_data_processed, dt):

        self.log.debug("%d bytes processed in %d seconds" % (amount_data_processed,
                                                             dt))
        if dt < 1.0:
            self.log.debug("Rate: N/A")
        else:
            data_rate = amount_data_processed / dt
            rate_string = sizeof_fmt(data_rate) + 'ps'
            self.log.debug("Rate: %s" % (rate_string))

    def _process_chosen_dataset(self):
        """This will process the dataset in chunks, but will wait until end of run
        chunks -1 means go forever"""
        # Used for benchmarking
        start_time = time.time()

        amount_data_processed = 0

        waittime = 1  # s

        # int rounds down
        min_time_index = int(self.input.get_min_time() / self.chunk_size)
        current_time_index = min_time_index

        search_for_more_data = True

        while (search_for_more_data):
            if self.input.has_run_ended():
                # Round up
                self.log.info("Data taking has ended; processing remaining data.")
                max_time_index = math.ceil(
                    self.input.get_max_time() / self.chunk_size)
                search_for_more_data = False
            else:
                # Round down
                max_time_index = int(self.input.get_max_time() / self.chunk_size)

            if max_time_index > current_time_index:
                for i in tqdm(range(current_time_index, max_time_index)):
                    t0 = (i * self.chunk_size)
                    t1 = (i + 1) * self.chunk_size

                    self.log.debug('Processing [%f s, %f s]' % (t0 / 1e8,
                                                                t1 / 1e8))

                    amount_data_processed += self._process_time_range(t0,
                                                                      t1 + self.padding,
                                                                      self.padding)

                    self._print_stats(amount_data_processed,
                                      time.time() - start_time)

                processed_time = (max_time_index - current_time_index)
                processed_time *= self.chunk_size / 1e8
                self.log.info("Processed %d seconds; searching for more data." % processed_time)
                current_time_index = max_time_index
            else:
                self.log.debug('Waiting %f seconds' % waittime)
                time.sleep(waittime)
                start_time = time.time()
                amount_data_processed = 0

        if self.delete_collection_when_done:
            self.drop_collection()

    def _process_time_range(self, t0, t1):
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
        reduction_factor = 100
        n = int(np.ceil((t1 - t0) / reduction_factor))
        cch.setup(n)

        # Every data doc has a start time and end time.  These ranges are used
        # later to compute overlaps with event ranges.
        doc_ranges = np.zeros((len(data_docs), 2), dtype=np.int32)

        for i, doc in enumerate(data_docs):
            time_correction = doc['time'] - t0

            samples = get_samples_from_doc(doc, self.input.is_compressed)
            doc['size'] = samples.size * 2
            # Record time range of these samples
            doc_ranges[i] = (time_correction / reduction_factor,
                             (time_correction + samples.size) / reduction_factor)

            cch.add_samples(samples, time_correction, reduction_factor)
            size += doc['size']

        #sum_data = cch.get_sum()

        self.log.debug("Size of data process in bytes: %d", size)

        # If no data analyzed, return
        self.log.debug("Size of data analyzed: %d", size)
        if size == 0:
            self.log.debug('No data found in [%d, %d]' % (t0, t1))
            return 0

        ranges = cch.build_events(10000, # Threshold
                                  int(MAX_DRIFT / reduction_factor))


        #  One event has many samples, thus to mapping represented as samples -> event
        mappings = cch.overlaps(doc_ranges.flatten())
        events = []

        ranges *= reduction_factor
        ranges = np.uint64(t0) + ranges.astype(np.uint64)

        self.log.fatal('0 ranges')
        self.log.fatal(ranges)
        ranges.resize((int(ranges.size / 2), 2))
        self.log.fatal('1 ranges %d %d', t0, t1)
        self.log.fatal(ranges)
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
                    # Check for event that spans many search blocks.  This super event 'should'
                    # never happen.
                    if last['range'][1] > t1 and last['range'][0] < t1 - self.padding:
                        raise RuntimeError("Event spans two search blocks (mega-event?)")

                    if last['range'][0] > t0 + self.padding and last['range'][1] < t1:
                        events.append(last)  # Save event

                self.log.debug('\tEvent %d', mapping)
                last = {}
                last['cnt'] = int(mapping)
                last['compressed'] = self.input.is_compressed
                last['range'] = [int(ranges[mapping][0]),
                                 int(ranges[mapping][1])]
                last['docs'] = []
                last['size'] = 0

            last['docs'].append(data_docs[i])
            last['size'] += data_docs[i]['size']

        if last != None:
            # Check for event that spans many search blocks.  This super event 'should'
            # never happen.
            if last['range'][1] > t1 and last['range'][0] < t1 - self.padding:
                raise RuntimeError("Event spans two search blocks (mega-event?)")

            if last['range'][0] > t0 + self.padding and last['range'][1] < t1:
                events.append(last)  # Save event

        if len(events):
            self.log.error("Saving %d events" % len(events))
            self.output.write_events(events)
        else:
            self.log.debug("No events found between %d and %d." % (t0, t1))
        self.log.fatal("Discarded: (%d/%d) = %0.3f%%",
                       reduced_data_count,
                       (len(data_docs) - reduced_data_count),
                       100 * float(reduced_data_count) / (len(data_docs) - reduced_data_count))
        return size

    def drop_collection(self):
        self.input.get_db().drop_collection(self.input.get_collection_name())
