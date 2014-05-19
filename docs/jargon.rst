======
Jargon
======

* Event building - Event building refers processing a time block of data and turning this into DAQ events.
* Software trigger - the code within this software that determines which data should be saved.
* DAQ event - Contiguous time block that typically corresponds a particle interaction in the detector with a time
  range of to the maximum drift time.
* Occurence - The digitizers only send data when a threshold is crossed.  An occurence is just a continous (in time)
block of data for just one channel.  An event will be composed of many occurences.
* Sample - a 14-bit measurement from the digitizers corresponding to a 10-ns window