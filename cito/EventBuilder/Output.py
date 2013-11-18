__author__ = 'tunnell'

import logging

from cito.core import XeDB


class OutputCommon():
    def __init__(self):
        if 'OutputCommon' == self.__class__.__name__:
            raise ValueError('This is a base class %s',self.__class__.__name__)
        self.log = logging.getLogger(self.__class__.__name__)

    def write_event(self):
        raise NotImplementedError()


class MongoDBOutput(OutputCommon):
    """Write to MongoDB

    This class, I don't think, can know the event number since it events before it
    may still be being processed.
    """

    def __init__(self):
        OutputCommon.__init__(self)

        self._collection = None

    @property
    def event_number(self):
        return "Not set"

    @property
    def collection(self):
        if self._collection == None:
           self.log.warning("Using default output MongoDB collection")
           conn, my_db, collection = XeDB.get_mongo_db_objects()
           # Todo: move this logic to XeDB?
           self._collection = conn['output']['somerun']
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value


    def clean_event(self, event_data):
        """Clean so can mongo"""
        new_data = {}
        for channel, channel_data in event_data['data'].items():
            new_data[str(channel)] = {}
            for variable_name, variable_value in channel_data.items():

                new_data[str(channel)][variable_name] = variable_value.tolist() # todo: pickle/bson


        event_data['data'] = new_data

        if 'peaks' in event_data:
            event_data['peaks'] = event_data['peaks'].tolist()

        return event_data

    def write_events(self, event_data_list):
        cleaned_list = [self.clean_event(x) for x in event_data_list]
        self.collection.insert(cleaned_list)

