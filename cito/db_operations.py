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

import logging

from cliff.command import Command
from cliff.show import ShowOne
from cito.helpers import xedb, InterfaceV1724

class DBReset(Command):
    """Reset the database by dropping the default collection.
    """

    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(DBReset, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        collection_name = collection.name

        my_db.drop_collection(collection.name)
        error = my_db.error()
        if error:
            self.log.error(error)
        else:
            self.log.info('Collection dropped succesfully')

class DBRepair(Command):
    """Repair DB to regain unused space.

    MongoDB can't know how what to do with space after a document is deleted,
    so there can exist small blocks of memory that are too small for new
    documents but non-zero.  This is called fragmentation.  This command
    copies all the data into a new database, then replaces the old database
    with the new one.  This is an expensive operation and will slow down
    operation of the database.
    """

    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(DBRepair, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        collection_name = collection.name

        my_db.command('repairDatabase')
        error = my_db.error()
        if error:
            self.log.error(error)
        else:
            self.log.info('Collection repaired succesfully')



class DBCount(ShowOne):
    """Count docs in DB.
    """

    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(DBCount, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        columns = ['Number of documents']
        data = [collection.count()]

        return (columns, data)