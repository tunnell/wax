__author__ = 'tunnell'

from cito.helpers import waveform
import logging
import matplotlib.pyplot as plt
import numpy as np

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
        self.log = logging.getLogger(__name__)
        if 'OutputCommon' == self.__class__.__name__:
            raise ValueError('This is a base class')

    def write_data_range(self, t0, t1, data, peaks,
                         save_range):

        to_save_bool_mask = waveform.get_index_mask_for_trigger(t1 - t0, peaks,
                                                                range_around_trigger=(-1*save_range,
                                                                                      save_range))
        print('wtf %d' % len(to_save_bool_mask))

        event_ranges = waveform.split_boolean_array(to_save_bool_mask)

        for e0, e1 in event_ranges:
            e0 += t0
            e1 += t0
            print('evt range', e0, e1)

            for key, value in data.items():
                (d0, d1, num_board, num_channel) = key
                (indecies, samples) = value

                num_pmt = get_pmt_number(num_board, num_channel)

                if d1 < e0 or e1 < e0: # If true, no overlap
                    continue

                print('where', np.where(indecies == e0), np.where(indecies == e1))
                #print(np.where(indecies == e1))

                #for i, index in enumerate(indecies):
                #    if e0 < index < e1:
                #    print(i, index, num_pmt)



            # data[(start, stop, num_board, num_channel)] = (indecies, samples)




class MongoDBOutput(OutputCommon):
    """Write to MongoDB

    This class, I don't think, can know the event number since it events before it
    may still be being processed.
    """
    pass

class HDF5Output(OutputCommon):
    """Write an HDF5 output.  This is a standard scinece format.

    This must know event numbers.
    See, e.g., http://www.hdfgroup.org/HDF5/
    """
    pass

class EpsOutput(OutputCommon):
    def plot(self, t0, t1, peak_indecies, results, save_range):
        fig = plt.figure(figsize=(7,5))
        #plt.title('Time from %d till %d' % (t0, t1))
        plt.plot(results['indecies'], results['samples'])
        plt.xlabel("Time [10 ns adc steps]")
        plt.ylabel("Sum charge [adc counts]")

        if t0 is not None and t1 is not None:
            plt.xlim((t0, t1))

        for peak_i in peak_indecies:
            peak_index = results['indecies'][peak_i]
            peak_value = results['samples'][peak_i]

            plt.vlines(peak_index, 0, peak_value, colors='r')
            plt.hlines(peak_value, peak_index - save_range, peak_index + save_range, colors='r')

        plt.savefig('peak_finding_%s_%s.eps' % (str(t0), str(t1)))
        plt.close(fig)
        #plt.show()

