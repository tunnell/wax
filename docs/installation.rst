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

Be sure to have the basics required to install code::

    $ sudo apt-get install -y build-essential git libatlas-base-dev gfortran libsnappy-dev libsnappy1 #mongodb-dev libboost-all-dev


Numpy and Scipy dependencies
----------------------------

Install the dependencies for scientific libraries in python::

    $ sudo apt-get build-dep -y python3-numpy
    $ sudo apt-get build-dep -y python3-scipy
    $ sudo apt-get build-dep -y python-matplotlib
    $ sudo apt-get install python-scitools



Installing Wax
===============

Up to this point, you've been installing the dependencies of `wax`.  However, installing `wax` itself is easy.  At the
command line, using 'easy_install' or 'pip', install `wax`::

    $ pip install git+https://github.com/tunnell/wax.git

This line also installs all the Python dependencies of `wax`. If you observe a problem, please submit a bug report.


