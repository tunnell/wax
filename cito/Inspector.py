"""For analyzing single documents
"""

import bson
from cito.CommandsBase import CitoShowOne
from cito.core import XeDB
import matplotlib.pyplot as plt

class TriggerInspector(CitoShowOne):
    """Inspect information about trigger event."""

    def get_parser(self, prog_name):
        """Be able to specify trigger index"""
        parser = super(TriggerInspector, self).get_parser(prog_name)

        parser.add_argument("-i", "--index", type=int, help="Trigger index", required=True)


        return parser

    def take_action(self, parsed_args):
        conn, my_db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname)

        # TODO: move into XeDB
        collection = conn['output']['somerun']
        self.log.info('Searching for trigger event %d' % parsed_args.index)
        #doc = collection.find("{}")
        doc = collection.find_one({'evt_num': parsed_args.index})

        output = []
        output.append(('Event number:', doc['evt_num']))

        output.append(('Range [10 ns]:', doc['range']))
        output.append(('Range [us]:', [i/100 for i in doc['range']]))

        output.append(('Span [10 ns]:', (doc['range'][1] - doc['range'][0])))
        output.append(('Span [us]:', (doc['range'][1] - doc['range'][0])/100))

        output.append(('Peaks:', doc['peaks']))
        output.append(('Channels with data:', str(doc['data'].keys())))

        x = doc['sum_data']['indices']
        y = doc['sum_data']['samples']

        plt.figure()
        plt.plot(x,y, 'o')

        for peak in doc['peaks']:
            plt.vlines(peak, 0, plt.ylim()[1])
        plt.hlines(plt.ylim()[1]*0.5, doc['range'][0], doc['range'][1])


        plt.figure()

        for channel, data in doc['data'].items():
            plt.plot(data['indices'], data['samples'], label=channel)
        plt.legend()
        plt.show()



        return zip(*output)
