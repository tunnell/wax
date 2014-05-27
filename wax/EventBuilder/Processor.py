"""
cito.core.EventBuilding
~~~~~~~~~~~~~~~~~~~~~~~

Event building converts time blocks of data (from different digitizer boards) into DAQ events.

Event building (see jargon) occurs by taking all the data from all the boards recorded during a time window and,
using some trigger logic, identifying independent events within this time window.  An EventBuilder class is defined
that performs the following sequential operations:

* Build sum waveform
* Using trigger algorithm, identify peaks in time.
* If there is no pileup (read further for pileup details), an event corresponds to a predefined time range before
  and after each peak.

More technically, a boolean array is created for each time sample, where True corresponds to a sample being saved
and false corresponds to an event being discarded.  These values default to false.  Two variables are defined by the
user: t_pre and t_post.  For each peak that the triggering algorithm identifies (e.g., charge above 100 pe), the
range [peak_i - t_pre, peak_i + t_post] is set to true  (see get_index_mask_for_trigger).  Subsequently, continuous
blocks of 'true' are called an event.

In other words, if two particles interact in the detector within a typical 'event window', then these two
interactions are saved as one event.  Identifying how to break up the event is thus left for postprocessing.  For
example, for peak_k > peak_i, if peak_i + t_post > peak_k - t_pre, these are one event.


"""

import math
import logging
import time

import pymongo
from tqdm import tqdm
from wax.Database import InputDBInterface, OutputDBInterface, ControlDBInterface
from wax import Configuration
from wax.EventBuilder.Tasks import process_time_range_task

from celery import result

__author__ = 'tunnell'



def sizeof_fmt(num):
    """input is bytes"""
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')


def sampletime_fmt(num):
    """num is in 10s of ns"""
    num *= 10
    for x in ['ns', 'us', 'ms']:
        if num < 1000.0:
            return "%3.1f %s" % (num, x)
        num /= 1000.0
    return "%3.1f %s" % (num, 's')


class Base:
    def __init__(self,
                 chunksize=Configuration.CHUNKSIZE,
                 padding=Configuration.PADDING,
                 threshold=Configuration.THRESHOLD):
        """None dataset means it will find it
        """

        self.log = logging.getLogger(__name__)
        self.input = None
        self.output = None
        self.controldb = None

        if chunksize <= 0:
            raise ValueError("chunksize <= 0: cannot analyze negative number of samples.")
        self.log.info("Using chunk size of %s" % sampletime_fmt(chunksize))
        self.chunksize = chunksize

        if padding < 0:
            raise ValueError("padding < 0: cannot analyze negative number of samples.")
        if padding >= chunksize:
            self.warning("Padding is bigger than chunk?")
        self.log.info("Using padding of %s" % sampletime_fmt(padding))
        self.padding = padding
        self.threshold = threshold

        self.waittime = 1 # Wait 1 second, if no data around

        self.stats = { 'type' : 'waxster',
                       'count_completed' : 0,
                       'count_failed' : 0,
                      'count_processing' : 0,
                      'size_pass' : 0,
                      'size_fail' : 0,
                      'delay_average' : 0.0,
                      'delay_longest' : 0.0
                        }


    def _initialize(self, dataset=None, hostname='127.0.0.1'):
        """If dataset == None, finds a collection on its own"""
        self.controldb = ControlDBInterface.MongoDBControl(collection_name='stats',
                                                            hostname=hostname)

        self.input = InputDBInterface.MongoDBInput(collection_name=dataset,
                                                   hostname=hostname)
        if self.input.initialized:
            self.output = OutputDBInterface.MongoDBOutput(collection_name=self.input.get_collection_name(),
                                                          hostname=hostname)
        else:
            self.log.debug("Cannot setup output DB.")
            self.output = None

    def process_single_dataset(self, hostname, dataset):
        # def EventBuilderDatasetLooper(hostname, dataset, chunks, chunksize, padding):
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
        # def EventBuilderDatasetLooper(hostname, dataset, chunks, chunksize, padding):
        """This function makes lots of processing classes"""
        while True:
            try:
                self._initialize(hostname=hostname)  # Dataset=None means it finds one
            except pymongo.errors.ConnectionFailure as e:
                self.log.error(e)
                self.log.error("Cannot connect to mongodb.  Will retry in 10 seconds.")
                time.sleep(10)
                continue

            if not self.input.initialized:
                self.log.warning("No dataset available to process; waiting one second.")
                time.sleep(1)
            else:
                self._process_chosen_dataset()

    def _process_chosen_dataset(self):
        """This will process the dataset in chunks, but will wait until end of run
        chunks -1 means go forever"""

        self._startup()

        # int rounds down
        min_time_index = int(self.input.get_min_time()/self.chunksize)

        current_time_index = min_time_index
        search_for_more_data = True

        while (search_for_more_data):
            if self.input.has_run_ended():
                # Round up
                self.log.info("Data taking has ended; processing remaining data.")
                max_time_index = math.ceil(self.input.get_max_time() / self.chunksize)
                search_for_more_data = False
            else:
                # Round down
                max_time_index = int(self.input.get_max_time() / self.chunksize)

            # Rates should be posted by tasks to mongo?
            if max_time_index > current_time_index:
                for i in tqdm(range(current_time_index, max_time_index)):
                    t0 = (i * self.chunksize)
                    t1 = (i + 1) * self.chunksize

                    self.process(t0=t0, t1=t1 + self.padding,
                                 collection_name=self.input.get_collection_name(),
                                 hostname=self.input.get_hostname())

                self.send_stats()
                processed_time = (max_time_index - current_time_index)
                processed_time *= self.chunksize / 1e8
                self.log.info("Processed %d seconds; searching for more data." % processed_time)

                current_time_index = max_time_index
            else:
                self.log.debug('Waiting %f seconds' % self.waittime)
                self.send_stats()
                time.sleep(self.waittime)
                self.send_stats()

        self.send_stats()

        self._shutdown()
        #self.drop_collection()
        self.send_stats()

    def drop_collection(self):
        self.input.get_db().drop_collection(self.input.get_collection_name())

    def get_processing_function(self):
        raise NotImplementedError()

    def _print_stats(self, amount_data_processed, dt):

        self.log.debug("%d bytes processed in %d seconds" % (amount_data_processed,
                                                             dt))
        if dt < 1.0:
            self.log.debug("Rate: N/A")
        else:
            data_rate = amount_data_processed / dt
            rate_string = sizeof_fmt(data_rate) + 'ps'
            self.log.debug("Rate: %s" % (rate_string))

    def process(self, **kwargs):
        raise NotImplementedError()

    def send_stats(self, **kwargs):
        raise NotImplementedError()

    def _startup(self):
        pass

    def _shutdown(self):
        pass


class SingleThreaded(Base):
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.start_time = None

    def process(self, **kwargs):
        self.stats['count_completed'] += 1

        x = process_time_range_task(**kwargs)
        self.stats['count_completed'] += 1
        self.stats['size_pass'] += x[0]
        self.stats['size_fail'] += x[1]

        stop_time = time.time()

        self.stats['rate'] = self.stats['size_pass']/(stop_time-self.start_time)
        self.stats['duration'] = (stop_time-self.start_time)
        self.log.fatal("took %d secs" % (stop_time-self.start_time))
        self.log.fatal('rate %f' % self.stats['rate'])


    def send_stats(self):
        self.controldb.send_stats(self.stats)

    def _startup(self):
        self.start_time = time.time()



class Celery(Base):
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.results = result.ResultSet([])

    def process(self, **kwargs):
        self.results.add(process_time_range_task.delay(**kwargs))

    def send_stats(self):
        self.stats['count_completed'] = self.results.completed_count()
        self.stats['failed'] = self.results.failed()
        self.controldb.send_stats(self.stats)

    def _shutdown(self):
        self.log.fatal("Waiting for jobs to finish")

        start_time = time.time()
        for x in self.results.join(timeout=600):
            self.stats['size_pass'] += x[0]
            self.stats['size_fail'] += x[1]

        stop_time = time.time()
        self.stats['rate'] = self.stats['size_pass']/(stop_time-start_time)
        self.stats['duration'] = (stop_time-start_time)

        self.log.fatal("took %d secs" % (stop_time-start_time))
        self.log.fatal('rate %sps' % sizeof_fmt(self.stats['rate']))

