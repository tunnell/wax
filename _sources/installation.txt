============
Installation
============

Every attempt is made to make wax` as portable as possible and install in a wide range of environments.  However,
installation instructions are given for Ubuntu 12 LTS.


Installing Python3.3
====================

If you have Python 3.3, skip this.  This requires root access.

`wax`, due to the dependencies, is only tested on Python3.3.  To install this on Ubuntu 12 LTS, please run the
following, which is inspired from
`here <http://linuxg.net/how-to-install-python-3-3-on-ubuntu-13-04-12-10-and-12-04/>`_::

    sudo apt-get install python-software-properties
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install -y python3.3-complete
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O /tmp/ez_setup.py
    sudo python3.3 /tmp/ez_setup.py
    sudo easy_install-3.3 pip virtualenv==1.10


These commands need only be run once.


Installing system dependencies
==============================

Here we install the basics required to compile code, and some dependencies such as math libraries for later codes.  All commands that include `sudo` require root access to your machine.  If you don't have it, talk to the system administrator.

Compiler
--------

Be sure to have the basics required to install code::

    $ sudo apt-get install build-essential


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


Install mongoclient
-------------------

Install mongo c++ client::

    $ git clone https://github.com/mongodb/mongo-cxx-driver.git
    $ cd mongo-cxx-driver
    $ sudo scons install-mongoclient --sharedclient

Install boost
-------------

Install boost for boost python::

    $ sudo apt-get install libboost-all-dev

Preparing Python environment
============================

It is advised to install within a virtualenv::


    $ virtualenv-3.3 -p python3.3 waxenv
    $ cd waxenv
    $ source bin/activate

To avoid potential complications with the order in which python packages are installed, we recommend installing numpy
explicitly (i.e., scipy can be `annoying <annoying`:http://github.com/scipy/scipy/pull/453>`_)::

    $ easy_install numpy

Installing Wax
===============

Up to this point, you've been installing the dependencies of `wax`.  However, installing `wax` itself is easy.  At the
command line, using 'easy_install' or 'pip', install `wax`::

    $ pip install git+https://github.com/tunnell/wax.git


This line also installs all the Python dependencies of `wax`. If you observe a problem, please submit a bug report.


(Optional) Installing own MongoDB database
==========================================

You must install MongoDB or use an existing installation.  Please refer to their docs, but hints are here for Ubuntu::

    sudo apt-get -y install screen openssh-server
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
    sudo apt-get update
    sudo apt-get -y install mongodb-10gen
    sudo service mongodb restart

