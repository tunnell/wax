============
Installation
============

Every attempt is made to make 'cito' as portable as possible and install in a wide range of environments.  Nevertheless,
 the scientific libraries that 'cito' relies on can sometimes cause installation problems.  For users who are
 unaccustomed to working with NumPy, SciPy, and Cython, it is recommended that they install
 "Anaconda":https://store.continuum.io/cshop/anaconda/, which includes all common Python packages.  The exact
 dependencies of cito can be found in the file requirements.txt.

.. important::
    cito only works with Python3.

Installing Anaconda
===================


Instally snappy
===============

Please install snappy, which is a compression library from Google.  The concept behind the library is when data is
being transferred over a network, the CPU is normally doing nothing.  Therefore, if we use the CPU a little, we can
reduce the data size and send the data quicker.

If it is not already installed, please install the snappy code, which can be found
'here':http://code.google.com/p/snappy/.

.. hint::
    For Ubuntu users, there is a package::


    $ sudo apt-get install libsnappy-dev

Please install python-snappy using your favorite Python package manager.  For example::

    $ pip install python-snappy

For python-snappy, you must install snappy library >= 1.0.2 (or revision 27) http://code.google.com/p/snappy/

Installing Cito
===============

At the command line::

    $ easy_install cito

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv cito
    $ pip install cito



Installing own MongoDB database
================================

You must install MongoDB or use an existing installation.  Please refer to their docs, but hints are here for Ubuntu::

    sudo apt-get -y install screen openssh-server
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
    sudo apt-get update
    sudo apt-get -y install mongodb-10gen
    sudo service mongodb restart

