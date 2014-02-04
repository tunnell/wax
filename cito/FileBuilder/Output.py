__author__ = 'tunnell'

import logging

from cito.core import XeDB


class OutputCommon():
    """Base class for all output
    """

    def __init__(self):
        if 'OutputCommon' == self.__class__.__name__:
            raise ValueError('This is a base class %s',
                             self.__class__.__name__)
        self.log = logging.getLogger(self.__class__.__name__)

    def write_event(self):
        raise NotImplementedError()

    @property
    def event_number(self):
        return "Not set"

class MongoDBOutput(OutputCommon):
    """Write to MongoDB

    This class, I don't think, can know the event number since it events before it
    may still be being processed.
    """

    def __init__(self):
        OutputCommon.__init__(self)

        # MongoDB collection to put data in
        self._collection = None


    @property
    def collection(self):
        if self._collection is None:
            self.log.warning("Using default output MongoDB collection")
            conn, my_db, collection = XeDB.get_mongo_db_objects()
            # Todo: move this logic to XeDB?
            self._collection = conn['output']['somerun']
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    def mongify_event(self, event_data):
        """Convert the data into a format that the Mongo API can save

        The main reason this has to be done is because the Mongo API does not
        understand numpy arrays."""
        new_data = {}
        for channel, channel_data in event_data['data'].items():
            new_data[str(channel)] = {}
            for variable_name, variable_value in channel_data.items():

                # Convert numpy array to Python list
                new_data[str(channel)][variable_name] = variable_value.tolist()

        event_data['data'] = new_data

        if 'peaks' in event_data:
            event_data['peaks'] = event_data['peaks'].tolist()

        return event_data

    def write_events(self, event_data_list):
        """Save data to database
        """
        self.log.debug(event_data_list)
        mongofied_list = [self.mongify_event(x) for x in event_data_list]
        self.collection.insert(mongofied_list)
