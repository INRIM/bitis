Changes
*******

Release 0.5.0 (released 9-Dec-2013)
===================================

Feature added
-------------

* Embed y limits setting into plot method.
* Add method square for signal generation of a periodc square wave.
* Add a more fine control in correlation function computation.
* Add signal append method.
* Add method start, return signal start time.
* Add method end, return signal end time.
* Add method len, return signal change times sequence length.

Incompatible changes
--------------------

* Change start times computation in bin2pwn, serial_tx to minimize
  time elapse from start to first change.

Refactor
--------

* Change noise from method to function.
* Change examples for changed noise method.

Bug fixed
---------

* Fix 0.4.0 release changelog: missing changes.

Release 0.4.0 (released 2-Dec-2013)
===================================

Feature added
-------------

* Add signal split method.
* Add two signals join method.
* Add unittest for split and join.
* Add float times capability to BTS signals.

Incompatible changes
--------------------

* Uniformate pwm2bin arguments to bin2pwm methods.
* Add tscale=1. argument in bin2pwm.
* Change to tscale=1. argument in serial_tx.

Refactor
--------

* Rewrite jitter method.

Bug fixed
---------

* Fix slevel setup, signal start and end in bin2pwm.

Release 0.3.0 (released 11-Nov-2013)
====================================

Feature added
-------------

* Add async serial transmitter (bits.serial_tx method) from chars to BTS
  serial line signal.
* Add async serial receiver (bitis.serial_rx method) from BTS serial line
  to chars.
* Add async serial transmitter example: serial_tx.py.
* Add unittest for async serial tx and rx.
* Modified plot method: only 0,1 ticks on y axis.

Release 0.2.0 (released 4-Nov-2013)
===================================

Feature added
-------------

* Add PWM coder and decoder between a BTS signal (PWM) and a binary code.
* New correlation example.

Release 0.1.0 (released 29-Oct-2013)
====================================

* First release.
