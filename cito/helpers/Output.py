__author__ = 'tunnell'

from cito.helpers import waveform, xedb
import logging
import matplotlib.pyplot as plt
import numpy as np
import pymongo

def get_pmt_number(num_board, num_channel):
    channels_per_board = 8 # this used elsewhere?
    if num_board == 770:
        scale = 0
    elif num_board == 876:
        scale = 1
    else:
        raise ValueError('Bad module number %d' % num_board)
    return channels_per_board * scale + num_channel



class OutputCommon():
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        if 'OutputCommon' == self.__class__.__name__:
            raise ValueError('This is a base class')

        self.event_number = None

    def get_event_number(self):
        if self.event_number is None:
            self.event_number = 0
            return self.event_number
        else:
            self.event_number += 1
            return self.event_number

    def write_data_range(self, t0, t1, data, peaks, results,
                         save_range):

        all = True
        if not all:
            to_save_bool_mask = waveform.get_index_mask_for_trigger(t1 - t0, peaks,
                                                                    range_around_trigger=(-1*save_range,
                                                                                                save_range))
            event_ranges = waveform.split_boolean_array(to_save_bool_mask)

            print('ranges', event_ranges, np.where(to_save_bool_mask == True))

        else:
            event_ranges = [(0, t1 - t0)]

        for e0, e1 in event_ranges:
            e0 += t0
            e1 += t0

            evt_num = self.get_event_number()
            self.log.info('\tEvent %d: [%d, %d]', evt_num, e0, e1)

            erange = np.arange(e0, e1)

            to_save = {}

            for key, value in data.items():
                (d0, d1, num_board, num_channel) = key
                (indecies, samples) = value

                num_pmt = get_pmt_number(num_board, num_channel)
                #to_save[num_pmt*-1] = {'indecies' : indecies,
                #                    'samples' : samples}

                if d1 < e0 or e1 < d0: # If true, no overlap
                    continue

                # Overlap range must be contiguous
                overlap = np.intersect1d(np.arange(d0, d1), erange)

                s0 = np.where(indecies == overlap[0])[0][0]
                s1 = np.where(indecies == overlap[-1])[0][0]
                self.log.debug('\t\tData (PMT%d): [%d, %d]', num_pmt, d0, d1)

                to_save[num_pmt] = {'indecies' : indecies[s0:s1],
                                    'samples' : samples[s0:s1]}
            to_save['peaks'] = peaks
            to_save['sum'] = results

            self.write_event(to_save, evt_num, e0, e1)





class MongoDBOutput(OutputCommon):
    """Write to MongoDB

    This class, I don't think, can know the event number since it events before it
    may still be being processed.
    """

    def __init__(self):
        OutputCommon.__init__(self)

        self.c = pymongo.MongoClient(xedb.get_server_name())
        self.collection = self.c['output']['somerun']

    def get_event_number(self):
        return "Not set"

    def write_event(self, event_data):
        new_data = {}
        for key in event_data.keys():
            new_data[str(key)] = [event_data[key]['samples'].tolist(),
                                  event_data[key]['indecies'].tolist()]

        new_data['event_number'] = self.get_event_number()
        self.collection.insert(new_data)

class HDF5Output(OutputCommon):
    """Write an HDF5 output.  This is a standard scinece format.

    This must know event numbers.
    See, e.g., http://www.hdfgroup.org/HDF5/
    """
    pass

class EpsOutput(OutputCommon):
    def __init__(self):
        OutputCommon.__init__(self)
        self.fig = plt.figure(figsize=(7,5))

    def write_event(self, event_data, evt_num, e0, e1):
        self.log.debug('write event %d [%d, %d]', evt_num, e0, e1)
        plt.clf()
        #plt.title('Time from %d till %d' % (t0, t1))

        for key, value in event_data.items():
            if key == 'peaks':
                continue

            if key == 'sum':
                plt.plot(value['indecies'], value['samples'], 'r-', label='SUM')
            else:
                plt.plot(value['indecies'], value['samples'], 'b--')

        print(event_data)
        #plt.xlim(e0, e1)
        plt.xlabel("Time [10 ns adc steps]")
        plt.ylabel("Sum charge [adc counts]")
        plt.title(str(event_data['peaks']))
        plt.legend()
        found_peak = False
        if 'peaks' in event_data:
            for peak in event_data['peaks']:
                if e0 < peak < e1:
                    found_peak = True
                    self.log.error('peak! %d', peak)
                    plt.vlines(peak, 0, plt.ylim()[1])
                    #plt.hlines(plt.ylim()[1]/2, e0, e1)

        if not found_peak:
            self.log.error("Cannot find peak/trigger in event range.")


        plt.savefig('peak_finding_%d.eps' % evt_num)
        #plt.close(fig)
        #plt.show()

