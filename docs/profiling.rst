=========
Profiling
=========

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    29                                               @profile
    30                                               def process(self, t0, t1):
    31                                                   """Process a time chunk
    32
    33                                                   .. todo:: Must this know padding?  Maybe just hand cursor so can mock?
    34
    35                                                   :param t0: Initial time to query.
    36                                                   :type t0: int.
    37                                                   :param t1: Final time.
    38                                                   :type t1: int.
    39                                                   :returns:  int -- number of bytes processed
    40                                                   :raises: AssertionError
    41                                                   """
    42       200       840257   4201.3      1.6          data_docs = XeDB.get_data_docs(t0, t1)
    43       200      7056493  35282.5     13.8          data, size = Waveform.get_data_and_sum_waveform(data_docs, t1 - t0)
    44
    45                                                   # If no data analyzed, return
    46       200        16363     81.8      0.0          self.log.debug("Size of data analyzed: %d", size)
    47       200          507      2.5      0.0          if size == 0:
    48        44         7543    171.4      0.0              self.log.warning('No data found in [%d, %d]' % (t0, t1))
    49        44          150      3.4      0.0              return 0
    50
    51                                                   # Build events (t0 and t1 used only for sanity checks)
    52       156          283      1.8      0.0          try:
    53       156     42829573 274548.5     83.5              events = self.event_builder.build_event(data, t0, t1)
    54                                                   except:
    55                                                       logging.exception('Event building failed.')
    56
    57       156          414      2.7      0.0          if len(events):
    58       156       549137   3520.1      1.1              self.output.write_events(events)
    59                                                   else:
    60                                                       self.log.warning("No events found between %d and %d." % (t0, t1))
    61
    62       156          485      3.1      0.0          return size



    95% of time in trigger.threshold