import pickle
import gzip
import matplotlib.pyplot as plt

# Load the cito output file
f = gzip.open('cito_file.pklz', 'rb')

print("cito version:", pickle.load(f))

#  You have to read all the events beforehand to get at an event
# therefore it reads 'n' times to get to event 'n'
for i in range(10):
    doc = pickle.load(f)
f.close()

x = doc['data']['sum']['indices']
plt.plot(x, doc['data']['sum']['samples'], label='unsmoothed sum')
plt.plot(x, doc['data']['smooth']['samples'],
         '--',
         label='smooth sum')
for peak in doc['peaks']:
    # Plot peaks
    plt.vlines(peak, plt.ylim()[0], plt.ylim()[1])
plt.title('Range: %s, Peaks: %s' % (str(doc['range']), str(doc['peaks'])))
plt.legend()
plt.xlabel('Time [10 ns]')
plt.ylabel('Charge [ADC counts]')

# Make a figure with all channels
plt.figure()
for channel, data2 in doc['data'].items():
    plt.plot(data2['indices'], data2['samples'], label=channel)
plt.title('Range: %s, Peaks: %s' % (str(doc['range']), str(doc['peaks'])))
plt.legend()
plt.xlabel('Time [10 ns]')
plt.ylabel('Charge [ADC counts]')

# Show plots
plt.show()

