"""Celery tasks"""
import numpy as np

from celery import Celery
import pymongo
from wax import Configuration
import ebcore

# Specify mongodb host and datababse to connect to
BROKER_URL = 'mongodb://xedaqtest2:27017/jobs'

celery = Celery('EOD_TASKS',
                broker=BROKER_URL,
                backend=BROKER_URL)


@celery.task
def process_time_range_task(t0, t1,
                            collection_name, hostname,
                            threshold=Configuration.THRESHOLD,
                            compressed=True):

    reduction_factor = 100
    return ebcore.process_time_range_task(t0,
                                          t1,
                                          Configuration.MAX_DRIFT,
                                          Configuration.PADDING,
                                          threshold,
                                          reduction_factor,
                                          hostname,
                                          "input.dataset", "output.dataset",
                                          compressed)
#                                          "%s.%s" % (MongoDBInput.get_db_name(), collection_name),
#                                          "%s.%s" % (MongoDBOutput.get_db_name(), collection_name))

@celery.task
def clear_processed(t0, collection_name, hostname='127.0.0.1'):
    """Delete data up to t0
    """

    c = pymongo.MongoClient(hostname)
    c['input'][collection_name].remove({"time_max": {"$lt": t0}})

