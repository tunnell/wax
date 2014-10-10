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
from wax import Configuration
from wax.EventBuilder.Tasks import process_time_range_task
from io import StringIO

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
    """Base class processor

    This is the base class of the single-threaded and Celery-based processors.
    """
    def __init__(self,
                 chunksize=Configuration.CHUNKSIZE,
                 padding=Configuration.PADDING,
                 threshold=Configuration.THRESHOLD,
                 run_hostname=Configuration.HOSTNAME):
        # Logging
        self.buffer = StringIO()
        logging.basicConfig(filename='example.log',level=logging.DEBUG)
        logging.StreamHandler(self.buffer)
        self.log = logging.getLogger(__name__)


        # Chunksize
        if chunksize <= 0:
            raise ValueError("chunksize <= 0: cannot analyze negative number of samples.")
        self.log.info("Using chunk size of %s" % sampletime_fmt(chunksize))
        self.chunksize = chunksize

        # Padding
        if padding < 0:
            raise ValueError("padding < 0: cannot analyze negative number of samples.")
        if padding >= chunksize:
            self.warning("Padding is bigger than chunk?")
        self.log.info("Using padding of %s" % sampletime_fmt(padding))
        self.padding = padding

        # Threshold
        self.threshold = threshold

        # Time to wait if no data found
        self.waittime = 1  # Wait 1 second, if no data around

        run_port = 27017
        run_db_name = 'online'
        run_collection_name = 'runs'

        # We have a few DB connections:
        #  - run control
        #  - input
        #  - output
        #  - stats

        self.connections = {}

        self.run_collection = self.get_connection(run_hostname)[run_db_name][run_collection_name]

        self.query = {"name": {'$exists': True},
                 "starttimestamp": {'$exists': True},
                 "runmode": {'$exists': True},
                 "reader": {'$exists': True},
                'trigger.status' : 'waiting_to_be_processed',
                     "trigger.mode": {'$exists': True},
                 "processor": {'$exists': True},
                 "comments": {'$exists': True},
                 }

        self.log.info("Entering endless loop")
        while 1:
            self.log.fatal("WTF")
            to_process = list(self.run_collection.find(self.query))
            self.log.fatal(to_process)

            if len(to_process) == 0:
                self.log.warning("No dataset available to process; waiting %d second." % self.waittime)
                time.sleep(self.waittime)
            else:
                for run in to_process:
                    self.log.fatal("Processing %s" % run['name'])

                    self._process_chosen_run(run)


    def get_connection(self, hostname):
        if hostname not in self.connections:
            try:
                self.connections[hostname] = pymongo.Connection(hostname)

            except pymongo.errors.ConnectionFailure as e:
                self.log.fatal("Cannot connect to mongo at %s" % hostname)

        return self.connections[hostname]


    def process(self, **kwargs):
        raise NotImplementedError()



    def _process_chosen_run(self, run_doc):
        """This will process the dataset in chunks, but will wait until end of run
        chunks -1 means go forever"""
        self.buffer = StringIO()

        #print >> self.buffer, "Log output"

        rootLogger = logging.getLogger()

        self.logHandler = logging.StreamHandler(self.buffer)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logHandler.setFormatter(formatter)
        rootLogger.addHandler(self.logHandler)

        self.logHandler = logging.StreamHandler(self.buffer)
        self.log.addHandler(self.logHandler)

        self.log.info(run_doc)
        data_location = run_doc['reader']['storage_buffer']
        conn = self.get_connection(data_location["dbaddr"])
        db = conn[data_location["dbaddr"]]
        collection = db[data_location["dbcollection"]]

        sort_key = [('time', -1),
                    ('module', -1),
                     ('_id', -1)]

        collection.ensure_index(sort_key,
                                background=True)

        # int rounds down
        min_time_index = 0 # int(self.input.get_min_time() / self.chunksize)

        current_time_index = min_time_index
        search_for_more_data = True

        self.log.fatal("GOT HERE")

        while (search_for_more_data):

            doc = collection.find_one({},
                                           fields=['time'],
                                           sort=sort_key)

            max_time = 0
            if doc is not None and doc['time'] is not None:
                max_time = doc['time']

            if run_doc['reader']['data_taking_ended']:
                # Round up
                self.log.info("Data taking has ended; processing remaining data.")
                max_time_index = math.ceil(max_time / self.chunksize)
                search_for_more_data = False
            else:
                # Round down
                max_time -= 1e8
                max_time_index = int(max_time / self.chunksize) - 1
                max_time_index = max(max_time_index, 0)

            if max_time_index > current_time_index:
                for i in tqdm(list(range(current_time_index, max_time_index))):
                    t0 = (i * self.chunksize)
                    t1 = (i + 1) * self.chunksize

                    self.process(t0=t0, t1=t1 + self.padding,
                                 collection_name=self.input.get_collection_name(),
                                 hostname=self.input.get_hostname())

                processed_time = (max_time_index - current_time_index)
                processed_time *= self.chunksize / 1e8
                self.log.info("Processed %d seconds; searching for more data." % processed_time)

                current_time_index = max_time_index
            else:
                self.log.debug('Waiting %f seconds' % self.waittime)
                time.sleep(self.waittime)

            self.log.fatal('before')
            self.log.fatal(run_doc)
            run_doc = self.run_collection.find_one({'_id' : run_doc['_id']})
            self.log.fatal('after')
            self.log.fatal(run_doc)


        rootLogger.removeHandler(self.logHandler)

        self.logHandler.flush()
        self.buffer.flush()
        x = self.buffer.getvalue()
        self.log.fatal(x)

        run_doc['trigger']['status'] = 'processed'
        run_doc['trigger']['log'] = x
        self.run_collection.save(run_doc)


class SingleThreaded(Base):

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)


    def process(self, **kwargs):
        process_time_range_task(**kwargs)


class Celery(Base):

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.results = result.ResultSet([])

    def process(self, **kwargs):
        self.results.add(process_time_range_task.delay(**kwargs))
