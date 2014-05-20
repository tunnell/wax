=====================
Internal data formats
=====================

All of the data formats specified refer to how data is stored within MongoDB for the event builder and trigger.

Input database
==============

This data is input to the event builder and stored within a database called `input`.  There is a collection within this database for each dataset.  The dataset name follows the format `dataset_YYMMDD_HHMM`, where the second half is the start time: e.g., YY is the 14 if the dataset was created in 2014. Therefore, a collection called `data_140105_1414` contains the data for a dataset that started collection on January 5th, 2014 at 2:14 pm.

Within each collection, there are two types of documents:

* Control document - information about running conditions
* Data document - raw data

Control document
----------------

The control document contains information about the dataset.  The following
keys are expected:

* `_id`: a hex string used for internal bookkeeping within MongoDB.  It is different for every document.
* `compressed`: Binary value that determines if the data is compressed using `snappy <https://code.google.com/p/snappy/>`_
* `data_taking_ended`: Tells cito if data is still to be reported.  This is set to false during aquisition, and true at the end of the run. `cito` uses this to know when it should just process the rest of the data and not wait for new data.
* `modules`: List of modules.
* `runtype`
* `starttime`: the 64-bit start time in units of 10 ns.  This must be the smallest time seem in any of the input data documents.

Said differently, expect:

.. code-block:: javascript

    {
        "_id": hex_string,
        "compressed": bool,
        "data_taking_ended": bool,
        "modules" : [int]
        "runtype": string,
        "starttime": int,
    }

Though may also contain:

* `channelmap`: If present, this tells us which modules and channels correspond to the channels that should always be digitized: e.g., sum waveform, GPS signals, muon-veto trigger, etc..  It can also be used to determine the radial position of the PMTs hooked up to the channel therefore allowing more complicated triggering algorithms.
* `errors`: a string that contains any error messages
* `messages`: any information about the run
* `daqconfig`: the DAQ configuration file for the program that puts data into the input database.
* `user`: a string with the name of the user who started the run.
* `slowcontrol`: any information from the slow control that should be stored
  in the final output.


Data document
-------------

One data document is created per occurence.  Therefore, there is one document per channel when the channel self triggered (remember: there is zero suppression).  For every occurence, the data document contains:

* `_id`: a hex string used for internal bookkeeping within MongoDB.  It is different for every document.
* `module`: identifies the digitizer board.  For fake data, this is set to -1.
* `channel`: Channel number.
* `time`: 64-bit unsigned number in units of 10 ns.  This time corresponds to the same time of the data in this document.  Please begin at 1 second or something to prevent trigger trying to save data at negative times.
* `data`: An array of 16-bit unsigned numbers, corresponding to the actual data payload.  It is stored as a binary array.

Said differently, expect:

.. code-block:: javascript

    {
        "_id": hex_string,
        "module": int,
        "channel": int,
        "time": int,
        "data": binary,
    }

Given that we are using a NoSQL database, variables may be added.  However, the schema only requires the five fields above.  Examples of possible extra fields include:

* `evtnum`: event number from either MC or a processed format.  This is used
  for helping study the trigger efficiency.

..warning  If start time is too small, the DAQ will skip the first data chunk (~1s) to avoid trying to record data at negative times.  See FAQ.


Output database
===============

The output is stored in a database called, surprisingly, called `output`. This is output of the event builder and input to the file builder. Within it are collections named after datasets, much like the input database: e.g., `dataset_YYMMDD_HHMM`.  The format is:

* The `_id` field is a hex string used for internal bookkeeping within MongoDB.
  It is different for every document.
* `evt_num` is an integer event number (if one has been assigned).
* `range` is two 64-bit unsigned integers that correspond to the beginning and end of
  the trigger window in units of 10 ns.
* `compressed_doc` is binary data compressed with snappy and contains all the
  data that will go to file.  For more information, see :doc:`analyze_data`.

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

See :doc:`analyze_data`.