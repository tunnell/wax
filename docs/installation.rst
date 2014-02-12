============
Installation
============

Every attempt is made to make 'cito' as portable as possible and install in a wide range of environments.  However,
installation instructions are given for Ubuntu 12 LTS.


(Optional) Installing Python3.3
===============================

cito, due to the dependencies, is only tested on Python3.3.  To install this on Ubuntu 12 LTS, please run the
following, which is inspired from
`here <http://linuxg.net/how-to-install-python-3-3-on-ubuntu-13-04-12-10-and-12-04/>`_::

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install -y python3.3-complete
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O /tmp/ez_setup.py
    sudo python3.3 /tmp/ez_setup.py
    sudo easy_install-3.3 pip virtualenv==1.10


These commands need only be run once.


Installing system dependencies
==============================

Here we install the basics required to compile code, and some dependencies such as math libraries for later codes.

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


Install snappy
--------------

Please install `snappy 1.0.2 <http://code.google.com/p/snappy/>`_, which is a compression library from Google.  The concept
behind the library is when data is being transferred over a network, the CPU is normally doing nothing.  Therefore, if
we use the CPU a little, we can reduce the data size and send the data quicker.

.. hint::
    For Ubuntu users, there is a package::


    $ sudo apt-get install libsnappy-dev libsnappy1




(Optional) Preparing Python environment
=======================================

It is advised to install within a virtualenv::


    $ virtualenv-3.3 -p python3.3 citoenv
    $ cd citoenv
    $ source bin/activate

To avoid potential complications with the order in which python packages are installed, we recommend installing numpy
explicitly (i.e., scipy can be annoying)::

    $ pip install numpy

Installing Cito
===============

Up to this point, you've been installing the dependencies of cito.  However, installing cito itself is easy.  At the
command line, using 'easy_install' or 'pip', install 'cito'::

    $ easy_install cito


This line also installs all the Python dependencies of cito. If you observe a problem, please submit a bug report.

.. hint::  On Mac, if can't find headers for C extensions, "export CPLUS_INCLUDE_PATH=/opt/local/include/"

(Optional) Installing own MongoDB database
==========================================

You must install MongoDB or use an existing installation.  Please refer to their docs, but hints are here for Ubuntu::

    sudo apt-get -y install screen openssh-server
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
    sudo apt-get update
    sudo apt-get -y install mongodb-10gen
    sudo service mongodb restart

