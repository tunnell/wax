__author__ = 'tunnell'

from cito.helpers import waveform
import logging

class OutputCommon():
    def __init__(self):
        self.log = logging.getLogger(__name__)


    def write_data_range(self, t0, t1, data, peaks,
                         save_range):

        to_save_bool_mask = waveform.get_index_mask_for_trigger(t1 - t0, peaks,
                                                                range_around_trigger=(-1*save_range,
                                                                                      save_range))


        self.log.debug(to_save_bool_mask)





class MongoDBOutput(OutputCommon):
    pass

class HDF5Output(OutputCommon):
    pass

class JsonOutput(OutputCommon):
    pass

