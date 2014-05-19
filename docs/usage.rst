=====
Usage
=====

Wax presents a command line interface.


Starting the event builder and software trigger
===============================================

By default, the data processing is done continuously.  This means that (unless otherwise specified) the software will wait for new datasets and data.  The default options are good for most situations.  To start the event building (which includes a software trigger), the following command can be run::

	event-builder

However, this is meant to run as a daemon and should already be running.  This is what one must do to restart.

Analyzing data in output database
=================================

See the `wax-on` and `wax-off` commands, where on is for online and off is for offline.  Currently, it just makes plots, but can be expanded to do whatever you want.





