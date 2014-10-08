============
Installation
============

Every attempt is made to make wax` as portable as possible and install in a wide
range of environments.  However, installation instructions are given for Ubuntu
14 LTS.

`Anaconda <https://store.continuum.io/cshop/anaconda/>`_ is a bundle of
scientific software.  Install anaconda with Python3.4::

  $ wget http://repo.continuum.io/anaconda3/Anaconda3-2.1.0-Linux-x86_64.sh
  $ bash Anaconda3-2.1.0-Linux-x86_64.sh
  $ export PATH=~/anaconda3/bin:$PATH  # If installed in default location

Follow the instructions presented to the screen.  These commands need only be
run once.

Be sure to activate this Python environment to proceed.  If you type::

  $ python -V
  $ which python

You should see Python 3.4 as the version installed and that the location of
Python is whereever you installed Anaconda.


Installing system dependencies
==============================

Here we install the basics required to compile code, and some dependencies such as math libraries for later codes.  All commands that include `sudo` require root access to your machine.  If you don't have it, talk to the system administrator.

Be sure to have the basics required to install code::

    $ sudo apt-get install -y build-essential git libatlas-base-dev gfortran libsnappy-dev libsnappy1 libboost-all-dev



Numpy and Scipy dependencies
----------------------------

Mongo driver::

  $ git clone git@github.com:mongodb/mongo-cxx-driver.git
  $ #sudo scons install --sharedclient --prefix=/usr/local/
  $ sudo scons install-mongoclient --full --use-system-boost --sharedclient


Numpy and Scipy dependencies
----------------------------

Install the dependencies for scientific libraries in python::

    $ sudo apt-get build-dep -y python-numpy python-scipy python-matplotlib
    $ sudo apt-get install python-scitools


Installing Wax
===============

Up to this point, you've been installing the dependencies of `wax`.  However, installing `wax` itself is easy.  At the
command line, using 'easy_install' or 'pip', install `wax`::

    $ pip install git+https://github.com/tunnell/wax.git

This line also installs all the Python dependencies of `wax`. If you observe a problem, please submit a bug report.


