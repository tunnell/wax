============
Installation
============

Using Python3.

At the command line::

    $ easy_install cito

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv cito
    $ pip install cito


For python-snappy, you must install snappy library >= 1.0.2 (or revision 27) http://code.google.com/p/snappy/

To get dependencies right, can do::

  macports: py33-scipy py33-matplotlib py33-cython
  ubuntu: apt-get install cython build-essential python3 python-virtualenv python3-scipy python3-numpy emacs23-nox

(git if dev)


You must install MongoDB.  Please refer to their docs, but hints are here for Ubuntu::

    sudo apt-get -y install screen openssh-server
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
    sudo apt-get update
    sudo apt-get -y install mongodb-10gen
    sudo service mongodb restart