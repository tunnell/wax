from wax import Configuration
import waxcore
import time

def sizeof_fmt(num):
    """input is bytes"""
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')

t0 = time.time()

size = 0
for i in range(10):
    size += waxcore.process_time_range_task(2**28 * i, (i+1)*2**28,
                                           "input.dataset",
                                "output.dataset",
                                "localhost",
                                100,
                                18000,
                                Configuration.PADDING)
t1 = time.time()
rate = '%sps' % sizeof_fmt(size/(t1-t0))
print(sizeof_fmt(size), rate, t1-t0)
