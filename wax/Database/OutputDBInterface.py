__author__ = 'tunnell'

from wax.Database import DBBase


class MongoDBOutput(DBBase.MongoDBBase):
    @staticmethod
    def get_db_name():
        return 'output'
