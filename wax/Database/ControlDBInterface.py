"""Interface code to the stats data in MongoDB

Mainly used for django website
"""

from datetime import datetime
import time
from wax.Database import DBBase


class MongoDBControl(DBBase.MongoDBBase):

    """Read from MongoDB
    """

    def __init__(self, collection_name=None, hostname=DBBase.HOSTNAME):
        if collection_name == None:
            collection_name = 'stats'

        DBBase.MongoDBBase.__init__(self, collection_name, hostname)

        if self.initialized is False:
            self.log.debug("Cannot initialize control DB.")
            return

    @staticmethod
    def get_db_name():
        return 'online'

    def send_stats(self, data=None):
        if data == None:
            data = {}
        assert isinstance(data, dict)

        if 'time' not in data:
            data['time'] = time.time()
        if 'ratetoss' not in data:
            data['ratetoss'] = 0
        if 'rateout' not in data:
            data['rateout'] = 0
        data['createdAt'] = datetime.now()
        data['expiresAfterSeconds'] = 43200

        self.get_collection().insert(data, w=0)

