==========================
Frequently Asked Questions
==========================


Why does the event builder not analyze the first few seconds of data?
=====================================================================

The first 'chunk', which is defaulted to roughly 2 seconds (2e28 * 10 ns),
is skipped to avoid the event builder trying to find events before the time
zero.  Times within the code are unsigned numbers and this would be an integer
wrap around (or overflow error).

As an aside, events that happen exactly at t=0 are worthless from a physics
perspective because it is unknown what occurred before this event. Maybe some
 interaction caused the event at t=0 that wasn't recorded.