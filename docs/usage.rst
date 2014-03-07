=====
Usage
=====

Cito presents a command line interface, where you can see the possible commands by running `cito`::

	cito -h


Starting the event builder and software trigger
===============================================

By default, the data processing is done continuously.  This means that (unless otherwise specified) the software will wait for new datasets and data.  The default options are good for most situations.  To start the event building (which includes a software trigger), the following command can be run::

    cito process

However, to do more complicated things, you can see the help file that will say what command-line arguments there are::

    cito help process

where, for example, the hostname can be specified.


Starting the file builder
=========================

File building can performed by running the command::

    cito file builder

This will create a file called `cito_file.pklz`.  To understand how to analyze this, see :doc:`analyze_data`.

Similar to the event building command, there are command line arguments::

    cito help file builder

where, for example, the hostname can be specified.


Database commands
=================


To delete the input and output databases, the reset function can be used::

    cito reset

but this cannot be used during a run and deletes all the database indices that are used to speed up searches.

These commands can be used for the input and output databases individually::

    cito reset --db output


Use the help command to understand what command line arguments exist::

    cito help reset

To clear the `fragmented <http://en.wikipedia.org/wiki/Fragmentation_(computing)>`_ space in the database, a repair function is used. (The delete command does not free up space.)  However, this cannot be used during operation since it locks the database during the operation..::

    cito repair






