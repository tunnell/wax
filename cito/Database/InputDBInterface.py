import logging
from cito.Database.XeDB import get_sort_key

__author__ = 'tunnell'


def get_min_time(collection):
    """Get minimum time in collection.

    Args:
       collection (Collection):  A pymongo Collection that will be queried

    Returns:
       int:  A time in units of 10 ns

    """
    sort_key = get_sort_key()
    sort_key = [(x[0], pymongo.ASCENDING) for x in sort_key]

    cursor = collection.find({}, fields=['triggertime'], limit=1, sort=sort_key)

    doc = next(cursor)
    logging.error('trig time: %s' % str(doc))
    time = doc['triggertime']
    if time is None:
        raise ValueError("No time found when searching for minimal time")
    logging.debug("Minimum time: %d", time)
    return time