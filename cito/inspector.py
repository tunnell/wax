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

import argparse
import logging

import os

from cliff.show import ShowOne
from cito.helpers import xedb, InterfaceV1724


class Inspector(ShowOne):
    """Grab DAQ document from MongoDB and print it.

    A DAQ document contains the V1724 flash ADC data.  If data in the document is
    compressed, it will decompress it.
    """

    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(Inspector, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')
        parser.add_argument('--print', type=str,
                            choices=('data', 'nondata', 'all'),
                            default='all',
                            help='Print only certain keys within document(s)')
        parser.add_argument('--skip-checks', dest='checks', action='store_false',
                            help='Skip consistency checks on data.')

        subparser = parser.add_mutually_exclusive_group(required=True)
        subparser.add_argument('-n', '--newest', action='store_true',
                               help='Get newest DAQ document')
        subparser.add_argument('--id', type=str,
                               help='Get DAQ document by ID')
        subparser.add_argument('-r', '--random', action='store_true',
                               help='Grab random DAQ document')

    #args = parser.parse_args()  # Grab command line args

        #parser.add_argument('filename', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = xedb.get_mongo_db_objects(parsed_args.hostname)

        if parsed_args.newest:
            try:
                time = xedb.get_max_time(collection)
                doc = collection.find_one({'triggertime': time})
            except RuntimeError as e:
                self.log.fatal('Runtime error: %s' % e)
                doc = None
        elif parsed_args.random:
            doc = collection.find_one()
        else:  # must be by ID since these args in in mutually exclusive group
            doc = collection.find_one({'_id': parsed_args.id})

        if doc == None:
            self.log.fatal("No document found.")
            return ([], [])

        selection = parsed_args.print
        do_checks = parsed_args.checks

        output = []


        # For every key in the doc, which is like every 'variable'
        for key in doc:
            if key == 'data':  # For data, we have a special printing format
                if selection == 'nondata':
                    continue

                # Get data from doc (and decompress if necessary)
                data = xedb.get_data_from_doc(doc)

                # A try/except block to see if the InterfaceV1724 class throwns
                # any assertion exceptions when checking for data consistency.
                try:
                    if do_checks:
                        output.append(('data(good header?)',
                                       InterfaceV1724.check_header(data)))
                    output.append(('data(trigger time tag)',
                                   InterfaceV1724.get_trigger_time_tag(data)))

                    size = InterfaceV1724.get_event_size(data, do_checks)
                    output.append(('data(size from header in words)',
                                   size))

                    # Loop over 32-bits words
                    for i in range(int(len(data)/4)):
                        # Print out 8 hex characters. After printing, the rightmost
                        # character on the string corresponds to the 0th bit.  The
                        # leftmost then corresponds to the highest 31st bit.
                        word = InterfaceV1724.get_word_by_index(data, i, do_checks)
                        output.append(('data[%d]' % i,
                                      '%08x' % word))

                except AssertionError as e:
                    # AssertionErrors are thrown when checking, for example, header
                    # consistency of the data.
                    self.log.error('!!Bad data. Caught exception: ', e)

                    # This shouldn't happen since the interface was told not to
                    # raise assertion errors
                    if not do_checks:
                        raise e

            elif selection != 'data':  # If not 'data' and data-only printing off
                output.append((key, doc[key]))

        return zip(*output)

