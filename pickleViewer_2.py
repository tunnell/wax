import pickle
import gzip

import matplotlib.pyplot as plt
import numpy as np

#restore the object
f = gzip.open('testPickleFile.pklz', 'rb')
doc = None

#  You have to read all the events beforehand to get at an event
# therefore it reads 'n' times to get to event 'n'
for i in range(12):
    doc = pickle.load(f)
f.close()

print(doc)
print('Range:', doc['range'])

plt.title('Range: %s' % str(doc['range']))

plt.plot(doc['sum_data']['indices'],
         doc['sum_data']['samples'],
         label='smooth sum')


from cito.Trigger.PeakFinder import smooth

plt.plot(doc['sum_data']['indices'],
         smooth(doc['sum_data']['samples'], np.array([50]))[0],
         label='smooth sum')

for channel, data2 in doc['data'].items():
    if channel == 'sum': continue
    plt.plot(data2['indices'], data2['samples'], label=channel)
plt.legend()
plt.xlabel('Time [10 ns]')
plt.ylabel('Charge [ADC counts]')

import ROOT
f = ROOT.TFile('/Users/tunnell/Work/env/lowmassdm/data/ambe/xe100_120402_2000.root')
t = f.Get('T1')
t.AddFriend('T1')
t.AddFriend('T3')


list_name = 'tempList'
t.Draw(">>%s" % list_name, "TimeMicroSec > %f && TimeMicroSec < %f" % (doc['range'][0],
                                                                       doc['range'][1]),
       'entrylist')
e1 = ROOT.gDirectory.Get(list_name)
#t.SetEntryList(e1, "ne");
N_selected = e1.GetN()
print(N_selected)
for i in range(N_selected):
    t.GetEntry(e1.GetEntry(i))
    print(t.S2sTot)


plt.show()
