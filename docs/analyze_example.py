"""Example of how to use cito to analyze data
"""
import pickle
import numpy as np
import gzip
import matplotlib.pyplot as plt
from pylab import gca, Rectangle

# Load the wax output file
f = gzip.open('cito_file.pklz', 'rb')
print("wax version", pickle.load(f))
i = 0
while 1:
    print("Event %d" % i)
    doc = pickle.load(f)

    #  Subtract off beginning of range
    offset = doc['range'][0]
    x = doc['data']['sum']['indices'] - offset

    # Plot unsmoothed digital-sum waveform
    plt.plot(x, doc['data']['sum']['samples'],
             label='unsmoothed sum',
             drawstyle='steps-mid')

    # Plot smoothed digital-sum waveform
    plt.plot(x, doc['data']['smooth']['samples'], '--',
             drawstyle='steps-mid',
             label='smooth sum')

    # Add every peak
    for peak in doc['peaks']:
        # Plot peaks
        plt.vlines(peak - offset, plt.ylim()[0], plt.ylim()[1])

    plt.title('Evt %d, Range: %s, Peaks: %s' % (i, str(doc['range']), str(doc['peaks'])))
    plt.legend()
    plt.xlim(doc['range'][0] - offset, doc['range'][1] - offset)
    plt.xlabel('Time [10 ns]')
    plt.ylabel('Charge [ADC counts]')

    # Make a figure with all channel data
    plt.figure()

    for channel, data2 in doc['data'].items():
        if type(channel) == str and ('sum' in channel or 'smooth' in channel):
            linetype = '--'
        else:
            linetype = '-'
        plt.plot(data2['indices'] - offset , data2['samples'], linetype, label=channel)


    plt.title('Evt %d, Range: %s, Peaks: %s' % (i, str(doc['range']), str(doc['peaks'])))
    plt.legend()
    plt.xlim(doc['range'][0] - offset, doc['range'][1] - offset)
    plt.xlabel('Time [10 ns]')
    plt.ylabel('Charge [ADC counts]')
    plt.vlines(np.array(doc['range'], dtype=np.int64) - offset ,
               plt.ylim()[0],
               plt.ylim()[1],
               color='red')

    # Show plots
    plt.show()
    i += 1
f.close()

