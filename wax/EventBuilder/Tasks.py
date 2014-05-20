"""Celery tasks"""
import numpy as np

from celery import Celery
import _wax_compiled_helpers as cch
import logging
import snappy
from wax.Configuration import SAMPLE_TYPE, MAX_DRIFT, PADDING, THRESHOLD
from wax.Database.InputDBInterface import MongoDBInput
from wax.Database.OutputDBInterface import MongoDBOutput

#Specify mongodb host and datababse to connect to                                                                                              
BROKER_URL = 'mongodb://xedaqje.no-ip.biz:27017/jobs'

celery = Celery('EOD_TASKS',
                broker=BROKER_URL,
                backend=BROKER_URL)

def save_decision(events, last, t0, t1):
    if last != None:
        # Check for event that spans many search blocks.  This super event 'should'
        # never happen.
        if last['range'][1] > t1 and last['range'][0] < t1 - PADDING:
            raise RuntimeError("Event spans two search blocks (mega-event?)")

        if last['range'][0] > t0 + PADDING and last['range'][1] < t1:
            events.append(last)  # Save event

@celery.task
def process_time_range(t0, t1,
                        collection_name, hostname,
                        threshold=THRESHOLD):
    """Process a time chunk

    .. todo:: Must this know padding?  Maybe just hand cursor so can mock?

    collection_name
    hostname

    :param t0: Initial time to query.
    :type t0: int.
    :param t1: Final time.
    :type t1: int.
    :returns:  int -- number of bytes processed
    :raises: AssertionError
    """
    input = MongoDBInput(collection_name=collection_name,
                         hostname=hostname)

    if input.initialized:
        output = MongoDBOutput(collection_name=input.get_collection_name(),
                                    hostname=hostname)
    else:
        logging.debug("Cannot setup output DB.")
        raise RuntimeError()

    data_docs = input.get_data_docs(t0, t1)

    untriggered_size = 0
    reduction_factor = 100
    n = int(np.ceil((t1 - t0) / reduction_factor))
    cch.setup(n)

    # Every data doc has a start time and end time.  These ranges are used
    # later to compute overlaps with event ranges.
    doc_ranges = np.zeros((len(data_docs), 2), dtype=np.int32)

    for i, doc in enumerate(data_docs):
        time_correction = doc['time'] - t0

        samples = get_samples_from_doc(doc, input.is_compressed)
        doc['size'] = samples.size * 2
        # Record time range of these samples
        doc_ranges[i] = (time_correction / reduction_factor,
                         (time_correction + samples.size) / reduction_factor)

        assert type(time_correction) == int
        cch.add_samples(samples, time_correction, reduction_factor)
        untriggered_size += doc['size']

    #sum_data = cch.get_sum()

    logging.debug("Size of data process in bytes: %d", untriggered_size)

    # If no data analyzed, return
    logging.debug("Size of data analyzed: %d", untriggered_size)
    if untriggered_size == 0:
        logging.debug('No data found in [%d, %d]' % (t0, t1))
        return 0

    ranges = cch.build_events(threshold,  # Threshold
                              int(MAX_DRIFT / reduction_factor))

    #  One event has many samples, thus to mapping represented as samples -> event
    mappings = cch.overlaps(doc_ranges.flatten())
    events = []

    ranges *= reduction_factor
    ranges = np.int64(t0) + ranges.astype(np.int64)

    ranges.resize((int(ranges.size / 2), 2))
    reduced_data_count = 0

    last = None
    for i, mapping in enumerate(mappings):
        # Document has no event, then skip
        if mapping == -1:
            reduced_data_count += 1
            continue

        # If need to start event
        if last == None or last['cnt'] != mapping:
            save_decision(events, last, t0, t1)

            logging.debug('\tEvent %d', mapping)
            last = {}
            last['cnt'] = int(mapping)
            last['compressed'] = input.is_compressed
            last['range'] = [int(ranges[mapping][0]),
                             int(ranges[mapping][1])]
            last['docs'] = []
            last['size'] = 0

        last['docs'].append(data_docs[i])
        last['size'] += data_docs[i]['size']

    save_decision(events, last, t0, t1)

    if len(events):
        logging.info("Saving %d events" % len(events))
        output.write_events(events)
    else:
        logging.debug("No events found between %d and %d." % (t0, t1))

    triggered_size = 0
    for event in events:
        triggered_size += event['size']

    return triggered_size, (untriggered_size - triggered_size)


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