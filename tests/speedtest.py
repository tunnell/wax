import ebcore
import time
from wax import Configuration
from wax.EventBuilder.Processor import sizeof_fmt

t0 = time.time()

size = 0
for i in range(10):
    size += ebcore.process_time_range_task(Configuration.CHUNKSIZE * i,
                                            Configuration.CHUNKSIZE * (i+1),
                                            Configuration.MAX_DRIFT,
                                            Configuration.PADDING,
                                            Configuration.THRESHOLD,
                                            Configuration.HOSTNAME,
                                           "input.dataset",
                                            "output.dataset")

t1 = time.time()
rate = '%sps' % sizeof_fmt(size/(t1-t0))
print(sizeof_fmt(size), rate, t1-t0)

