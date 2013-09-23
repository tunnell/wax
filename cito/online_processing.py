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
import pymongo
from cito import db
import tasks
import sys
import time


if __name__ == "__main__":

    chunk_size = 2 ** 28 #10**9 # 0.01 second in units of 10 ns step
    padding = 0 # 10 ** 2 # 1 microsecond in units of 10 ns step

    conn, my_db, collection = db.get_mongo_db_objects()

    # Key to sort by so we can use an index for quick query
    sort_key = [
        ('triggertime', pymongo.DESCENDING),
        ('module', pymongo.DESCENDING)
    ]

    # Index for quick query
    collection.create_index(sort_key, dropDups=True)
    current_time_index = int(3735061640/chunk_size)

    # Loop until Ctrl-C or error
    while (1):
        # This try-except catches Ctrl-C and error
        try:
            # Non-sense query that is in index
            query = {"triggertime": {'$gt': 0}}

            max_time = db.get_max_time(collection)
            time_index = int(max_time / chunk_size)

            print(current_time_index)
            if time_index > current_time_index:
                for i in range(current_time_index, time_index):
                    t0 = (i * chunk_size - padding)
                    t1 = (i + 1) * chunk_size
                    print('Processing', t0, t1)
                    tasks.process(t0, t1)

                current_time_index = time_index
            else:
                print('.')
                time.sleep(0.1)
                #my_db.command('repairDatabase')
            #break
        except StopIteration:
            pass
        except ValueError as e:
            #print("ValueError:", e)
            raise # pass # This means no events left
        except pymongo.errors.OperationFailure as e:
            print('MongoDB error:', e)
        except KeyboardInterrupt:
            print("Ctrl-C caught so exiting.")
            sys.exit(0)
