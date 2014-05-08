======
Jargon
======


* Event building - Event building refers processing a time block of data and turning this into DAQ events.
* DAQ event - Contiguous time block that typically corresponds a particle interaction in the detector with a time
  range of to the maximum drift time.
* File builder - Take DAQ events and write them to a file.
* Occurence - The digitizers only send data when a threshold is crossed.  An occurence is just a continous (in time)
block of data for just one channel.  An event will be composed of many occurences.