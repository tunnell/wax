"""Interface code to the stats data in MongoDB

Mainly used for django website
"""

from datetime import datetime
import time
from wax.Database import DBBase


class DBStats(DBBase.MongoDBBase):
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

        data = data.copy()

        data['time'] = time.time()
        data['createdAt'] = datetime.now()
        data['expiresAfterSeconds'] = 43200

        self.get_collection().insert(data, w=0)
