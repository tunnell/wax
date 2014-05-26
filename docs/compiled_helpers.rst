================
Compiled Helpers
================

To make the software trigger run quick enough to keep up with high data rates,
parts of the code are written in C to make them fast.

There are essentially two steps to this code, which involves calls to three different functions.  This is `add_samples`, which is used to send occurences to the code.  Then event ranges are found using two function calls to `build_events` and `overlaps`.

.. sourcecode:: ipython

    In [69]: lines = plot([1,2,3])

    In [70]: setp(lines)
      alpha: float
      animated: [True | False]
      antialiased or aa: [True | False]
      ...snip


.. automodule:: _wax_compiled_helpers
   :members:
   :undoc-members: