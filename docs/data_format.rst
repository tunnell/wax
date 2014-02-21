=====================
Internal data formats
=====================

All of the data formats specified refer to how data is stored within MongoDB.

Input to Event Builder format
=============================

This data is input to the event builder.

The data input format is a BSON document.  Per digitizer board, a document is created that must contain the keys:

* Module: identifies the digitizer board
* Triggertime: This is a 64 bit number where the lower 32 bits are formed from the board time, and the upper 32 bits
  from the system clock.  Each step is 10 ns.  There is enough range with 64 bits to not overflow the clock for about
  10000 years, which from now was around when creation was in the Jewish calendar.  
* Data: The actual payload.  This is the raw Caen format (maybe compressed) and must be converted into a usable
  format.
* Zipped: Is the data compressed using `snappy <https://code.google.com/p/snappy/>`_?

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


Output from Event Builder, input to File Builder format
=======================================================

This is output of the event builder and input to the file builder.

* The `_id` field is a hex string used for internal bookkeeping within MongoDB.
* `evt_num` is an integer event number (if one has been assigned).
* `range` is two integers that correspond to the beginning and end of the trigger window.
* `compressed_doc` is binary data compressed with snappy and contains all the data that will go to file.  For more
  information, see :doc:`analyze_data`.

Said differently:

.. code-block:: javascript

    {
        "_id": hex_string,
        "evt_num": int,
        "range": [int, int],
        "compressed_doc": binary,
    }


File from File Builder  format
==============================

See :doc:`analyze_data`