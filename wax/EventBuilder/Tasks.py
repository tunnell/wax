"""Celery tasks"""
import numpy as np

from celery import Celery
import logging
import snappy
from wax import Configuration
#from wax.Database.InputDBInterface import MongoDBInput
#from wax.Database.OutputDBInterface import MongoDBOutput
#from wax.Database.ControlDBInterface import DBStats
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
