"""For analyzing single documents
"""

import bson

from cito.CommandsBase import CitoShowOne
from cito.core import InterfaceV1724, XeDB


class Inspector(CitoShowOne):
    """Grab DAQ document from MongoDB and print it.

    A DAQ document contains the V1724 flash ADC data.  If data in the document is
    compressed, it will decompress it.
    """

    def get_parser(self, prog_name):
        """Define what command line arguments we want this to be able to do"""
        parser = super(Inspector, self).get_parser(prog_name)

        parser.add_argument('--print', type=str,
                            choices=('data', 'nondata', 'all'),
                            default='all',
                            help='Print only certain keys within document(s)')

        subparser = parser.add_mutually_exclusive_group(required=True)
        subparser.add_argument('-n', '--newest', action='store_true',
                               help='Get newest DAQ document')
        subparser.add_argument('--id', type=str,
                               help='Get DAQ document by ID')
        subparser.add_argument('-r', '--random', action='store_true',
                               help='Grab random DAQ document')

        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = XeDB.get_mongo_db_objects(
            parsed_args.hostname)

        if parsed_args.newest:
            try:
                time = XeDB.get_max_time(collection)
                doc = collection.find_one({'triggertime': time})
            except RuntimeError as e:
                self.log.fatal('Runtime error: %s' % e)
                doc = None
        elif parsed_args.random:
            doc = collection.find_one()
        else:  # must be by ID since these args in in mutually exclusive group
            self.log.debug("Building BSON ID from string")
            id_bson = bson.objectid.ObjectId(parsed_args.id)
            self.log.debug("ID: %s", parsed_args.id)
            doc = collection.find_one({'_id': id_bson})

        if doc is None:
            self.log.fatal("No document found.")
            return ([], [])

        selection = parsed_args.print

        output = []

        # For every key in the doc, which is like every 'variable'
        for key in doc:
            if key == 'data':  # For data, we have a special printing format
                if selection == 'nondata':
                    continue

                # Get data from doc (and decompress if necessary)
                data = XeDB.get_data_from_doc(doc)
                self.log.debug("Data: %s", str(data))

                # A try/except block to see if the InterfaceV1724 class throwns
                # any assertion exceptions when checking for data consistency.
                try:
                    try:
                        output.append(('data(good header?)', InterfaceV1724.check_header(data)))
                    except AssertionError:
                        output.append(('data(good header?)', False))

                    try:
                        output.append(('data(trigger time tag)',
                                       InterfaceV1724.get_trigger_time_tag(data)))
                    except AssertionError:
                        output.append(('data(trigger time tag)', False))

                    try:
                        size = InterfaceV1724.get_block_size(data)
                        output.append(('data(size from header in words)',
                                       size))
                    except AssertionError:
                        output.append(('data(size from header in words)', False))

                    try:
                        result = InterfaceV1724.get_waveform(data, 10000)
                        output.append(('data(processing exception)',
                                       'none'))
                        print(result)
                    except Exception as e:
                        output.append(('data(processing exception)',
                                       str(e)))

                    # Loop over 32-bits words
                    for i in range(int(len(data) / 4)):
                        # Print out 8 hex characters. After printing, the rightmost
                        # character on the string corresponds to the 0th bit.  The
                        # leftmost then corresponds to the highest 31st bit.
                        word = data[i]
                        output.append(('data[%d]' % i,
                                       '%08x' % word))

                except AssertionError as e:
                    # AssertionErrors are thrown when checking, for example, header
                    # consistency of the data.
                    self.log.error('!!Bad data. Caught exception: ', e)

                    # This shouldn't happen since the interface was told not to
                    # raise assertion errors
                    raise e

            # If not 'data' and data-only printing off
            elif selection != 'data':
                output.append((key, doc[key]))

        return zip(*output)
