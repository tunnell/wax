.. :changelog:

History
-------

2.1 (2014-04-24)
++++++++++++++++

* Mock pymongo and include test on real data
* BUG: Didn't include the time offset of search window

2.0 (2014-04-22)
++++++++++++++++

* Rename project to wax
* Remove cliff dependency since underutilized
* Processing of waveforms is now done in C using swig

1.9 (2014-03-19)
++++++++++++++++

* BUG: Not all PMT data was being written to output file (if PMT had lots of hits)
* Begining of testing and general cleanup
* Speed up some math routines

1.8 (2014-03-05)
++++++++++++++++

* Fix major bug that included rejected data
* Continuous processing
* Implemented 'padding' to deal with events near search window edges
* General documentation and command-line description cleanup for usage.
* Remove interactive mode that was confusing users.
* Fix CTRL-C behavior.
* Find minimal time rather than relying on control doc.

1.7 (2014-03-05)
++++++++++++++++

* Major refactoring of DB interface due to interface changes to input DB
* Include control documents - see docs
* Allow auto discovery of datasets

1.6 (2014-02-27)
++++++++++++++++

* Add version number to output
* Fix some issues with how timing was defined in input.
* Speed up after profiling

1.5 (2014-02-24)
++++++++++++++++

* Reactor DB interfaces now that there are two (output, input)
* Improve DB access commands within cito
* Improve help

1.4 (2014-02-19)
++++++++++++++++

* Switch from convolution to filtering using a butter filter.
* Expansion of command line argument options.
* Fixed bug that resulted in filtering/convolution occuring over the entire 1s window.

1.1 (2014-02-12)
++++++++++++++++

* Fix some major bugs associated with 1.0 due to misplaced files and failed refactoring.

1.0 (2014-02-10)
++++++++++++++++

* Beta release reading for use and testing.

0.1 (2013-08-11)
++++++++++++++++

* Alpha release based on testing in Bern.