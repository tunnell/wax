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
"""Grab DAQ document and print it.

A DAQ document contains the V1724 flash ADC data.  If data in the document is
compressed, it will decompress it.
"""
import db
import argparse
import binascii

def pretty_print_daq_doc(doc, selection='all'):
    print("Doc: {")

    for key in doc:
        pre_text = '\t %s : ' % key
        if key == 'data':
            if selection == 'nondata':
                continue
            print(pre_text)
            data = db.get_data_from_doc(doc)
            hex_string = binascii.b2a_hex(data)
            for i in range(0, len(data), 8):
                print('\t\t%08x' % int((hex_string[i:i+8]), 16))
            ','
        elif selection != 'data':
            print(pre_text, doc[key],',')
    print('}')




if __name__ == "__main__":
    #-db DATABSE -u USERNAME -p PASSWORD -size 20
    parser = argparse.ArgumentParser(description=__doc__)

    subparser = parser.add_mutually_exclusive_group(required=True)
    subparser.add_argument("-s", "--single", action='store_true',
                           help="Grab single event")

    parser.add_argument("-db", "--hostname", help="Database name",
                        type=str,
                        default='127.0.0.1')

    parser.add_argument('-n', '--newest', action='store_true',
                        help='Get newest event')
    parser.add_argument('-p', '--print', type=str,
                        choices=('data', 'nondata', 'all'),
                        default='all',
                        help='Print only certain keys within document(s)')

    args = parser.parse_args()

    if args.single:
        conn, my_db, collection = db.get_mongo_db_objects(args.hostname)

        if args.newest:
            time = db.get_max_time(collection)
            doc = collection.find_one({'triggertime' : time})
        else:
            doc = collection.find_one()
        pretty_print_daq_doc(doc, args.print)
    else:
        parser.print_help()