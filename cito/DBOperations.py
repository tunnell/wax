"""Commands for the command line interface for DB operations.

All of these commands are simple enough that they don't rely too
much on XeDB.  Maybe these commands should be moved there though?
"""

from cito.core import XeDB
from cito.core.main import CitoShowOne


class DBReset(CitoShowOne):
    """Reset the database by dropping the default collection.

    Warning: this cannot be used during a run as it will kill the DAQ writer.
    """

    def take_action(self, parsed_args):
        conn, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)
        db.drop_collection(collection.name)
        return self.get_status(db)


class DBPurge(CitoShowOne):
    """Delete/purge all DAQ documents without deleting collection.

    This can be used during a run.
    """

    def take_action(self, parsed_args):
        conn, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname,
                                                         selection='input')
        self.log.debug("Purging all documents")
        collection.remove({})
        return self.get_status(db)


class DBRepair(CitoShowOne):
    """Repair DB to regain unused space.

    MongoDB can't know how what to do with space after a document is deleted,
    so there can exist small blocks of memory that are too small for new
    documents but non-zero.  This is called fragmentation.  This command
    copies all the data into a new database, then replaces the old database
    with the new one.  This is an expensive operation and will slow down
    operation of the database.
    """

    def take_action(self, parsed_args):
        conn, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)
        db.command('repairDatabase')
        return self.get_status(db)


