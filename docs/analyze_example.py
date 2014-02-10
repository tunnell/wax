import pickle
import gzip

import matplotlib.pyplot as plt


#restore the object
f = gzip.open('testPickleFile.pklz', 'rb')
doc = None

#  You have to read all the events beforehand to get at an event
# therefore it reads 'n' times to get to event 'n'
for i in range(10):
    doc = pickle.load(f)
f.close()

print(doc)
print('Range:', doc['range'])

plt.title('Range: %s' % str(doc['range']))

plt.plot(doc['sum_data']['indices'],
         doc['sum_data']['samples'],
         label='smooth sum')

for channel, data2 in doc['data'].items():
    if channel == 'sum': continue
    plt.plot(data2['indices'], data2['samples'], label=channel)
plt.legend()
plt.xlabel('Time [10 ns]')
plt.ylabel('Charge [ADC counts]')
plt.show()

