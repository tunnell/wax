======================================
Code for Intelligent Triggering Online
======================================

.. image:: https://badge.fury.io/py/cito.png
  :target: http://badge.fury.io/py/cito
    
.. image:: https://travis-ci.org/tunnell/cito.png
  :target: https://travis-ci.org/tunnell/cito

.. image:: https://pypip.in/d/cito/badge.png
  :target: https://crate.io/packages/cito


This code constitutes a framework for software triggering intended for particle and astroparticle physics experiments with pre-trigger data rates of 300 MB/s.  The code scales to 300 MB/s by using celery over numerous computers, but the goal is to have a single thread be able to process a few MB/s.

* Free software: BSD license
* Documentation: http://tunnell.github.io/cito/

Usage
-----

To run `cito`::

    $ pip install cito
    $ cito process
    $ cito file builder

See the usage section in the documentation for more information.

Features
--------

* Processing of Caen V1724 blocks
* Scalable with celery distributed task queue
* Flexible trigger windows and thresholds
* MongoDB data backend
* First open-source software trigger framework

Overview
--------

The program `cito` consists of two main components: data processing and data recording.  