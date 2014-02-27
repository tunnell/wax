=====
Usage
=====

Cito presents a command line interface, where you can see the possible commands by running `cito`::

	cito -h


Event Builder
=============

Event building can performed by running the command::

    cito process

To know what the command line arguments are, run::

    cito help process

where, for example, the hostname can be specified.


File Builder
=============

File building can performed by running the command::

    cito file builder

Similar to the event building command, there are command line arguments::

    cito help file builder

where, for example, the hostname can be specified.


Clear Database Options
==============

To keep the database, but delete all the documents run::

    cito purge

which can be run during data taking.

To delete the database, the reset function can be used::

    cito reset

but this cannot be used during a run and deletes all the database indices that are used to speed up searches.

These commands can be used for the input and output databases individually.  Use the help command to understand what command line arguments exist::

    cito help reset

To clear the `fragmented <http://en.wikipedia.org/wiki/Fragmentation_(computing)>`_ space in the database, a repair function is used. (The delete command does not free up space.)  However, this cannot be used during operation since it locks the database during the operation..::

    cito repair






