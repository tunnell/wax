=====
Usage
=====

Wax presents a command line interface.


Starting the event builder and software trigger
===============================================

By default, the data processing is done continuously.  This means that (unless otherwise specified) the software will wait for new datasets and data.  The default options are good for most situations.  To start the event building (which includes a software trigger), the following command can be run::

	event-builder

However, this is meant to run as a daemon and should already be running.  This is what one must do to restart.


===============
Starting Celery
===============

When Celery is running, all wax does is ship jobs off to Celery.  Celery nodes
must pick these events up.

To start Celery once `wax` is installed, run::

  celery -A wax.EventBuilder.Tasks worker



