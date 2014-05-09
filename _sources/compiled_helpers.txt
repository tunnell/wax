================
Compiled Helpers
================

To make the software trigger run quick enough to keep up with high data rates,
parts of the code are written in C to make them fast.

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