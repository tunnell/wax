==========================
Frequently Asked Questions
==========================


Why does the event builder not analyze the first few seconds of data?
=====================================================================

Data is analyzed in chunks of about 1 second.  For events near the boundary of two chunks, some logic is required to determine which chunk 'owns' the event.  Remember: there are windows around events in addition to these chunks, so it requires a bit of logic.  There is overlap between chunks.  From t=0 till the overlap size (i.e. [0, t_overlap]) is from the -1 event, so is not saved.

What is the mega event?
=======================

 If there is too much pile up, this software will start combining all the events together into one super large event.  If this happens for too long, then something outside the normal laws of the Universe is happening and the DAQ stops.