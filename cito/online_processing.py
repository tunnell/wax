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
"""Online processing executable
"""

__author__ = 'tunnell'
import logging
import sys
import time

import pymongo
from cliff.command import Command

from cito.core import XeDB


class Process(Command):

    """Process data from DB online
    """

    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(Process, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        parser.add_argument('--chunksize', type=int,
                            help="Size of data chunks to process [10 ns step]",
                            default=2 ** 17)
        parser.add_argument('--padding', type=int,
                            help='Padding to overlap processing windows [10 ns step]',
                            default=10 ** 2)
        parser.add_argument('--flush', action='store_true',
                            help='Constantly flush the DB of new documents (single thread)')
        parser.add_argument('--single', action='store_true',
                            help='Disable Celery and single thread')
        parser.add_argument('--wait-time', type=float, dest='waittime',
                            help='Time to sleep in seconds if no documents to process',
                            default=0.1)

        return parser

    def take_action(self, parsed_args):
        chunk_size = parsed_args.chunksize
        padding = parsed_args.padding

        conn, my_db, collection = XeDB.get_mongo_db_objects(
            parsed_args.hostname)

        # Key to sort by so we can use an index for quick query
        sort_key = [
            ('triggertime', pymongo.DESCENDING),
            ('module', pymongo.DESCENDING)
        ]

        # Index for quick query
        collection.create_index(sort_key, dropDups=True)
        current_time_index = int(XeDB.get_min_time(collection) / chunk_size)
        self.log.debug('Current time index %d', current_time_index)

        # Loop until Ctrl-C or error
        while (1):
            # This try-except catches Ctrl-C and error
            try:
                max_time = XeDB.get_max_time(collection)
                time_index = int(max_time / chunk_size)

                self.log.debug('Previous chunk %d' % current_time_index)
                self.log.debug('Current chunk %d' % time_index)
                if time_index > current_time_index:
                    for i in range(current_time_index, time_index):
                        t0 = (i * chunk_size - padding)
                        t1 = (i + 1) * chunk_size
                        self.log.info('Processing %d %d' % (t0, t1))
                        if parsed_args.flush:
                            pass  # tasks.flush(t0, t1)
                        else:
                            if parsed_args.single:
                                pass  # tasks.process(t0, t1)
                            else:
                                pass  # tasks.process.delay(t0, t1)

                    current_time_index = time_index
                else:
                    self.log.debug('Waiting %f seconds' % parsed_args.waittime)
                    time.sleep(parsed_args.waittime)
                    # my_db.command('repairDatabase')
                    # break
            except StopIteration:
                pass
            except ValueError as e:
                self.log.exception(e)
                raise  # pass # This means no events left
            except KeyboardInterrupt:
                self.log.info("Ctrl-C caught so exiting.")
                sys.exit(0)
