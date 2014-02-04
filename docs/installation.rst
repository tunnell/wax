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
  ubuntu: apt-get install cython build-essential python3 python-virtualenv python3-scipy python3-numpy 

(git if dev)