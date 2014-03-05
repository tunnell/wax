"""Commands for the command line interface for DB operations.

All of these commands are simple enough that they don't rely too
much on XeDB.  Maybe these commands should be moved there though?
"""
import logging
from cito.Database import InputDBInterface, OutputDBInterface
from cliff.show import ShowOne
import pymongo


class CitoDBShowOne(ShowOne):
    """Base class for all DB commands.

    Handles logging, descriptions, and common fuctions.
    """
    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(ShowOne, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address. Can be IP or DNS address.",
                            type=str,
                            default='127.0.0.1')
        parser.add_argument("--db", help="Input or output DB (or all) on which to perform operation.",
                            type=str, required=True,
                            choices=['input', 'output', 'all'])

        return parser

    def get_status(self, db):
        """Return DB errors, if any"""
        error = db.error()
        if error:
            self.log.error(error)
            data = error
        else:
            data = 'ok'
        return data

    def take_action(self, parsed_args):
        results = []

        conn = pymongo.Connection(parsed_args.hostname)

        if parsed_args.db =='input' or parsed_args.db == 'all':
            db = conn[InputDBInterface.MongoDBInput.get_db_name()]
            result = self.take_action_wrapped(conn, db)
            results.append(['Input: Requested operation result',result])
            results.append(['Input: DB status', self.get_status(db)])

        if parsed_args.db =='output' or parsed_args.db == 'all':
            db = conn[OutputDBInterface.MongoDBOutput.get_db_name()]
            result = self.take_action_wrapped(conn, db)
            results.append(['Output: Requested operation result', result])
            results.append(['Output: DB status', self.get_status(db)])

        return zip(*results)


    def take_action_wrapped(self, conn, db):
        raise NotImplementedError()


class DBDelete(CitoDBShowOne):
    """Delete the database by dropping it.

    Warning: this cannot be used during a run as it will kill the DAQ writer.
    """

    def take_action_wrapped(self, conn, db):
        self.log.info("Resetting DB.")
        conn.drop_database(db.name)
        return 'Reset'


class DBRepair(CitoDBShowOne):
    """Repair DB to regain unused space.

    MongoDB can't know how what to do with space after a document is deleted,
    so there can exist small blocks of memory that are too small for new
    documents but non-zero.  This is called fragmentation.  This command
    copies all the data into a new database, then replaces the old database
    with the new one.  This is an expensive operation and will slow down
    operation of the database.
    """

    def take_action_wrapped(self, conn, db):
        self.log.info("Repairing DB.")
        db.command('repairDatabase')
        return 'Repaired'



