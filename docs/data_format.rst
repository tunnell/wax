============
Data formats
============

Here reviewed are data formats

Input
=====

The data input format is a BSON document.  Per digitizer board, a document is created that must contain the keys:

* Module: identifies the digitizer board
* Triggertime: This is a 64 bit number where the lower 32 bits are formed from the board time, and the upper 32 bits
  from the system clock.  Each step is 10 ns.  There is enough range with 64 bits to not overflow the clock for about
  10000 years, which from now was around when creation was in the Jewish calendar.  
* Data: The actual payload.  This is the raw Caen format (maybe compressed) and must be converted into a usable
  format.
* Zipped: Is the data compressed using snappy?

Given that we are using a NoSQL database, variables may be added.  However, the schema only requires the four fields
above.

As of 22/October/2013, an example document is:

.. code-block:: javascript

    {
        "_id": ObjectId("525186149d7a330faeae9d68"),
        "insertsize": NumberInt(46154),
        "module": NumberInt(876),
        "triggertime": NumberLong(1055247666930),
        "zipped": true,
        "datalength": NumberInt(549),
        "data": "<Mongo Binary Data>"
    }

.. code-block:: javascript

    {
       "_id": ObjectId("525186149d7a330faeae9d65"),
       "insertsize": NumberInt(46151),
       "module": NumberInt(770),
       "triggertime": NumberLong(1055247650512),
       "zipped": true,
       "datalength": NumberInt(752),
       "data": "<Mongo Binary Data>"
    }


Ouput format
============


* Processed: sum waveform (feature request)
* Raw data: TBD format