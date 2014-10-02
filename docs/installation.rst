============
Installation
============

Every attempt is made to make wax` as portable as possible and install in a wide range of environments.  However,
installation instructions are given for Ubuntu 12 LTS.

Install anaconda with Python3.4

These commands need only be run once.


Installing system dependencies
==============================

Here we install the basics required to compile code, and some dependencies such as math libraries for later codes.  All commands that include `sudo` require root access to your machine.  If you don't have it, talk to the system administrator.

Compiler, boost, scons
--------

Be sure to have the basics required to install code::

    $ sudo apt-get install build-essential libboost1.55-all-dev scons

Mongo
-----

Install mongo client::

    $ git clone https://github.com/mongodb/mongo-cxx-driver.git
    $ cd mongo-cxx-driver
    $ git checkout 26compat
    $ scons --full --libpath=/usr/lib/x86_64-linux-gnu --sharedclient --use-system-boost

Fortran and linear algebra libraries
------------------------------------

Install a ATLAS (linear algebra routine) and Fortran compiler::

    $ sudo apt-get install -y libatlas-base-dev gfortran



Numpy and Scipy dependencies
----------------------------

Install the dependencies for scientific libraries in python::

    $ sudo apt-get build-dep -y python3-numpy
    $ sudo apt-get build-dep -y python3-scipy
    $ sudo apt-get build-dep -y python-matplotlib
    $ sudo apt-get install python-scitools


Install snappy
--------------

Please install `snappy 1.0.2 <http://code.google.com/p/snappy/>`_, which is a compression library from Google.  The concept
behind the library is when data is being transferred over a network, the CPU is normally doing nothing.  Therefore, if
we use the CPU a little, we can reduce the data size and send the data quicker.

.. hint::
    For Ubuntu users, there is a package::


    $ sudo apt-get install libsnappy-dev libsnappy1

Installl Mongo dev
------------------

Mongo::

    $  sudo apt-get install mongodb-dev


Install boost
-------------

Install boost for boost python::

    $ sudo apt-get install libboost-all-dev


Installing Wax
===============

Up to this point, you've been installing the dependencies of `wax`.  However, installing `wax` itself is easy.  At the
command line, using 'easy_install' or 'pip', install `wax`::

    $ pip install git+https://github.com/tunnell/wax.git

This line also installs all the Python dependencies of `wax`. If you observe a problem, please submit a bug report.


