==============
Usage examples
==============

Logic operations
----------------

This simple example shows some logic operations supported by the **BITIS**
module.

.. literalinclude:: ../examples/xor_logic.py
    :linenos:
    :language: python
    :lines: 30-

Correlation Function
--------------------

The following example shows the plotting of two random signals and their
correlation function.

.. literalinclude:: ../examples/correlation.py
    :linenos:
    :language: python
    :lines: 30-

This is the plotting result.

.. image:: ../examples/correlation.png

Serial signal
-------------

The following example shows the signal of an asynchronous serial interface
coding the ASCII character "U" with 8 character bits, odd parity, 2 stop bits
and 50 baud tranmitting speed.

.. literalinclude:: ../examples/serial_tx.py
    :linenos:
    :language: python
    :lines: 30-

This is the plotting result. The signal is represented as exiting from a UART
device at TTL level. This kind of signal is logically inverted with respect to
a RS-232 signal. The x axis units are seconds. 

.. image:: ../examples/serial_tx.png

* S: start bit.
* 0/1: character bits.
* P: parity bit.
* E: stop bits.

Phase lockin
------------

The following example demonstrate a phase recovery from a disturbed periodic
signal whose undisturbed original is known. The original signal is a
square wave of 50 cycles @1Hz, 50 % duty cycle. A gaussian jitter is added
to the original signal change times and the result is xored with noise pulses
to simulate transmission line disturbances.

.. literalinclude:: ../examples/lockin.py
    :linenos:
    :language: python
    :lines: 30-

The plot shows the original, the
disturbed signal and the correlation among them, correlation that reaches a
maximum when the original has that same phase of the disturbed original. 

.. image:: ../examples/lockin.png
