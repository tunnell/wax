"""For analyzing single documents
"""
import itertools

import bson

import matplotlib.pyplot as plt

from cito.core import XeDB
from cito.core.main import CitoShowOne


class OutputDocInspector(CitoShowOne):
    """Inspect information about trigger event."""

    def get_parser(self, prog_name):
        """Be able to specify trigger index"""
        parser = super(OutputDocInspector, self).get_parser(prog_name)

        parser.add_argument("-i", "--index", type=int, help="Trigger index", required=True)

        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)

        # TODO: move into XeDB
        collection = conn['output']['somerun']
        index = parsed_args.index
        self.log.info('Searching for trigger event %d' % index)

        doc = collection.find_one({'evt_num': index})

        output = []

        try:

            output.append(('Event number', doc['evt_num']))

            output.append(('Range [10 ns]', doc['range']))
            output.append(('Range [us]', [i / 100 for i in doc['range']]))

            output.append(('Span [10 ns]', (doc['range'][1] - doc['range'][0])))
            output.append(('Span [us]', (doc['range'][1] - doc['range'][0]) / 100))

            output.append(('Peaks', doc['peaks']))
            output.append(('Channels with data', str(doc['data'].keys())))

            scale = 100

            x = [i / scale for i in doc['sum_data']['indices']]
            y = doc['sum_data']['samples']

            plt.figure()
            plt.plot(x, y, 'o')

            for peak in doc['peaks']:
                plt.vlines(peak / scale, 0, plt.ylim()[1])
            plt.hlines(plt.ylim()[1] * 0.5, doc['range'][0] / scale, doc['range'][1] / scale)
            plt.xlabel('$\mu$s')
            plt.savefig('sum_%d.eps' % index)
            output.append(('Sum plot', 'sum_%d.eps' % index))

            plt.figure()
            for channel, data in doc['data'].items():
                plt.plot([i / scale for i in data['indices']], data['samples'], label=channel)
            plt.xlabel('$\mu$s')
            plt.legend()

            plt.savefig('channels_%d.eps' % index)
            output.append(('Channel plot', 'channels_%d.eps' % index))
        except:
            self.log.exception('fail to inspect')

        return zip(*output)


class InputDocInspector(CitoShowOne):
    """Grab DAQ document from MongoDB and print it.

    A DAQ document contains the V1724 flash ADC data.  If data in the document is
    compressed, it will decompress it.
    """

    def get_parser(self, prog_name):
        """Define what command line arguments we want this to be able to do"""
        parser = super(InputDocInspector, self).get_parser(prog_name)

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


class InputDBInspector(CitoShowOne):
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
            return ','.join(map(str, lst)), []

        step = lst[1] - lst[0]
        for i, x, y in zip(itertools.count(1), lst[1:], lst[2:]):
            if y - x != step:
                if i > 1:
                    return self.formatter2(lst[0], lst[i], step), lst[i + 1:]
                else:
                    return str(lst[0]), lst[1:]
        return self.formatter2(lst[0], lst[-1], step), []

    def re_range(self, lst):
        result = []
        while lst:
            partial, lst = self.helper(lst)
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