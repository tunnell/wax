"""Commands for the command line interface for DB operations.

All of these commands are simple enough that they don't rely too
much on XeDB.  Maybe these commands should be moved there though?
"""

from bson.code import Code
from cito.CommandsBase import CitoShowOne
from cito.core import XeDB
import itertools

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
        conn, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)
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


class DBInspector(CitoShowOne):

    """Show statistics on DB collection
    """

    @staticmethod
    def formatter2(start, end, step):
        if step > 1:
            return '{}-{}:{}'.format(start, end, step)
        else:
            return '{}-{}'.format(start, end)

    def helper(self, lst):
        if len(lst) == 1:
            return str(lst[0]), []
        if len(lst) == 2:
            return ','.join(map(str,lst)), []

        step = lst[1] - lst[0]
        for i,x,y in zip(itertools.count(1), lst[1:], lst[2:]):
            if y-x != step:
                if i > 1:
                    return self.formatter2(lst[0], lst[i], step), lst[i+1:]
                else:
                    return str(lst[0]), lst[1:]
        return self.formatter2(lst[0], lst[-1], step), []

    def re_range(self, lst):
        result = []
        while lst:
            partial,lst = self.helper(lst)
            result.append(partial)
        return ','.join(result)

    def take_action(self, parsed_args):
        conn, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)
        columns = ['Number of documents']
        data = [collection.count()]

        modules = collection.distinct('module')
        modules.sort()
        columns.append('Modules')
        data.append(self.re_range(modules))

        columns.append('Module count')
        data.append(str(len(collection.distinct('module'))))

        columns.append('Missing modules')
        modules = collection.distinct('module')
        missing_modules = [i for i in range(min(modules), max(modules)) if i not in modules]
        data.append(self.re_range(missing_modules))

        columns.append('Missing modules count')
        data.append(len(missing_modules))

        return columns, data


class DBDuplicates(CitoShowOne):

    """Find duplicate data and print their IDs.

    Search through all the DAQ document's data payloads (i.e., 'data' key) and
    if any of these are identical, list the keys so they can be inspected with
    the document inspector.  A Map-Reduce algorithm is used so the results are
    stored in MongoDB as the 'dups' collection.
    """

    def take_action(self, parsed_args):
        conn, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)

        map_func = Code("function () {"
                        "  emit(this.data, 1); "
                        "}")

        reduce_func = Code("function (key, values) {"
                           "return Array.sum(values);"
                           "}")

        # Data to return
        columns = []
        data = []

        result = collection.map_reduce(map_func, reduce_func, "dups")
        for i, doc in enumerate(result.find({'value': {'$gt': 1}})):
            columns.append('Dup[%d] count' % i)
            data.append(doc['value'])

            for j, doc2 in enumerate(collection.find({'data': doc['_id']})):
                columns.append('Dup[%d][%d] ID' % (i, j))
                data.append(doc2['_id'])

        if len(columns):
            columns = ['Status'] + columns
            data = ['Duplicates found'] + data
        else:
            columns = ['Status']
            data = ['No duplicates']

        return columns, data
