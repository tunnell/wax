=====
Usage
=====

Cito presents a command line interface, where you can see the possible commands by running `cito`.

	cito -h


Event Builder
=============

Event building can performed by running the command.

    cito process

To know what the command line arguments are, run:

    cito help process

where, for example, the hostname can be specified.


File Builder
=============

File building can performed by running the command.

    cito file builder

Similar to the event building command, there are command line arguments

    cito help file builder

where, for example, the hostname can be specified.


Clear Database Options
==============

To keep the database, but delete all the documents run:

    cito purge

To delete the database the reset function can be used:

    cito reset

This can be used for the input and output database individually, command line arguments with:

    cito help reset

To clear the space in the database a repair function is used. The delete command does not free up space.

    cito repair






