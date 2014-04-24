===
WAX
===

.. image:: https://badge.fury.io/py/wax.png
  :target: http://badge.fury.io/py/wax
    
.. image:: https://travis-ci.org/tunnell/wax.png
  :target: https://travis-ci.org/tunnell/wax

.. image:: https://pypip.in/d/wax/badge.png
  :target: https://crate.io/packages/wax


This code constitutes a framework for software triggering intended for particle and astroparticle physics experiments with pre-trigger data rates of 300 MB/s.  The code scales to 300 MB/s by using celery over numerous computers, but the goal is to have a single thread be able to process a few MB/s.

* Free software: BSD license
* Documentation: http://tunnell.github.io/wax/

Usage
-----

To run `wax`::

    $ pip install git+https://github.com/tunnell/wax.git
    $ wax-off --help

See the usage section in the documentation for more information.

Features
--------

* Processing of Caen V1724 blocks
* Scalable with celery distributed task queue
* Flexible trigger windows and thresholds
* MongoDB data backend
* First open-source software trigger framework
* Data analysis online `wax-on` and offline `wax-off`

Overview
--------

The program `wax` consists of two main components: data processing (wax process) and data recording (wax file builder).  