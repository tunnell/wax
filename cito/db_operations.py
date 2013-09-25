# cito - The Xenon1T experiments software trigger
# Copyright 2013.  All rights reserved.
# https://github.com/tunnell/cito
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of the Xenon experiment, nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Commands for the command line interface for DB operations.
"""

import logging

from cliff.show import ShowOne
from cito.helpers import xedb, InterfaceV1724


class DBBase(ShowOne):
    """Base class for all DB commands.

    Handles logging, descriptions, and common fuctions.
    """
    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(DBBase, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        return parser

    def get_status(self, db):
        """Return DB errors, if any"""
        columns = ['Status']
        error = db.error()
        if error:
            self.log.error(error)
            data = [error]
        else:
            data = ['success']
        return columns, data

class DBReset(DBBase):
    """Reset the database by dropping the default collection.
    """


    def take_action(self, parsed_args):
        conn, db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        # The pymongo call
        db.drop_collection(collection.name)

        # TODO: Maybe purge celery too?
        #from celery.task.control import discard_all
        #discard_all()

        return self.get_status(db)

class DBRepair(DBBase):
    """Repair DB to regain unused space.

    MongoDB can't know how what to do with space after a document is deleted,
    so there can exist small blocks of memory that are too small for new
    documents but non-zero.  This is called fragmentation.  This command
    copies all the data into a new database, then replaces the old database
    with the new one.  This is an expensive operation and will slow down
    operation of the database.
    """

    def take_action(self, parsed_args):
        conn, db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        # The actual pymongo call
        db.command('repairDatabase')

        return self.get_status(db)



class DBCount(DBBase):
    """Count docs in DB.
    """


    def take_action(self, parsed_args):
        conn, db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        columns = ['Number of documents']
        data = [collection.count()]

        return columns, data

