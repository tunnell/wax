===============
Starting Celery
===============

When Celery is running, all wax does is ship jobs off to Celery.  Celery nodes
must pick these events up.

To start Celery once `wax` is installed, run::

  celery -A wax.EventBuilder.Tasks worker


