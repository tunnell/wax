================
Compiled Helpers
================

To make the software trigger run quick enough to keep up with high data rates,
parts of the code are written in C to make them fast.

There are essentially two steps to this code, which involves calls to three different functions.  This is `add_samples`, which is used to send occurences to the code.  Then event ranges are found using two function calls to `build_events` and `overlaps`.


Times should be uint64_t.  Samples should be uint32_t.

.. cpp:class:: waxcore

    .. cpp:function:: int ProcessTimeRangeTask(uint64_t t0, uint64_t t1,
                                               uint64_t max_drift,
                                               uint64_t padding,
                                               uint16_t threshold,
                                               char* hostname,
                                               char* mongo_input_location,
                                               char* mongo_output_location)

    .. cpp:function:: Shutdown()

        Free all memory.  Call before destruction.

        :return: None