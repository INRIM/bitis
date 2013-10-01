#!/usr/bin/python
# .+
# .context    : Binary Signal Processing
# .title      : Vectorial Binary Signal Processing Library
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	26-Sep-2013
# .copyright  :	(c) 2013 Fabrizio Pollastri
# .license    : GNU Lesser General Public License (see below)
#
# This file is part of "VEBIS".
#
# VEBIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# VEBIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with VEBIS. If not, see <http://www.gnu.org/licenses/>.
#
#
# TODO
# - extend vbs format to support odd number of pulses/edges
# - check tests for inverted signals
# .-


#### import required modules

import copy             # object copy support
import math             # mathematical support
import random           # random generation


#### classes

class Signal:
    """ Implements the concept of "Vectorial Binary Signal", a memory
    representation of a binary signal by a vector or list filled with the
    timing of signal changes (signal edges). This representation is useful
    when the signal has a low rate of change with respect to the sampling
    period. In this case, the representation is very compact in memory.
    The first element of signal sequence has always change time = 0. The
    sequence can be shifted in time by specifying a time offset. The signal
    level before the first change is specified by a initial value. The
    signal level after the last change is equal to initial value, if changes
    are even, otherwise is inverted. """

    # a test signal with a sequence of primes as timing changes
    TEST_SIGNAL = [0,1,2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61]


    def __init__(self,signal=[],initial_value=0,time_offset=0,
            time_scale=1000):

        # sequence of signal changes times
        if signal:
            self.signal = signal
        else:
            self.signal = []
        # signal level before the first change
        self.initial_value = initial_value
        # number of signal changes
        try:
            self.length = len(signal)
        except:
            self.length = 0
        # time offset affecting all signal changes
        self.time_offset = time_offset
        # time scale of changes time (1=1s)
        self.time_scale = time_scale


    def __str__(self):
       
        descr = '%s\n' % self.__class__
        descr += '  signal: %s\n' % self.signal
        descr += '  initial value: %d\n' % self.initial_value
        descr += '  length: %d\n' % self.length
        descr += '  time offset: %d\n' % self.time_offset
        descr += '  time scale: %d' % self.time_scale

        return descr


    def test(self):
        """ Fill current signal object with a test signal. Previous signal
        data is destroyed. """

        # fill current signal changes and its length attribute
        self.signal = self.TEST_SIGNAL
        self.length = len(self.TEST_SIGNAL)


    def clone(self):
        """ Returns a copy with the same attributes/values of current the
        instance. """

        return copy.deepcopy(self)


    def offset(self,time_offset=None):
        """ Get/Set the time offset (s) for all signal changes. If
        *time_offset* is not specified, returns the time offset value (int)i
        stored in the signal object. Otherwise, set it. """

        if time_offset:
            self.time_offset = time_offset * self.time_scale
        else:
            return float(self.time_offset) / self.time_scale


    def reverse(self):
        """ Reverse the signal edge sequence: last edge becomes the first
        and viceversa.Time intervals between all edges are preserved.
        Returns the same input signal object with the updated signal. """

        # simplify var access
        signal = self.signal
        length = self.length

        # reversal time adjusting constant
        time_adjust = signal[-1]

        # reverse edges times
        for i in range(length-1,-1,-1):
            signal[i] = time_adjust - signal[i]

        # edges sequence needs to have ascending times
        signal.sort()


    def jitter(self,jitter_stddev=0):
        """ Add a gaussian jitter to *signal* with the given standard deviation
        *jitter_stddev* (s) and zero mean. The first and last signal edges are
        unchanged. The jitter is added to the current signal istance. """

        # convert to proper time scale
        jitter_stddev *= self.time_scale

        # simplify access
        signal = self.signal
        length = self.length

        # add jitter to signal edges
        for edge in range(1,length-1):
            # if current edge has room to be moved forward or back, add jitter.
            if signal[i+1] - signal[i-1] > 2:
                signal[i] += int(random.gauss(0.0,jitter_stddev))
                # limit jitter range inside prevoius and next edges
                if signal[i] <= signal[i-1]:
                    signal[i] = signal[i-1] + 1
                elif signal[i] >= signal[i+1]:
                    signal[i] = signal[i+1] - 1


    def noise(self,time_start,time_end,freq_mean=1,freq_stddev=1,
            width_mean=0.1,width_stddev=0.1):
        """ Fill current signal object with disturbing pulses. Pulses time
        domain extends from *time_start* to *time_end* seconds. Pulses
        frequency and width follow a gaussian distribution: *freq_mean* and
        *freq_stddev* are the given mean and standard deviation of frequency
        in hertz, *width_mean* and *width_stddev* are the given mean and
        standard deviation of the pulse width in seconds (1 level).
        Previous signal data is destroyed. """

        # convert to proper time scale
        time_end *= self.time_scale
        freq_mean *= self.time_scale
        freq_stddev *= self.time_scale
        width_mean *= self.time_scale
        width_stddev *= self.time_scale

        # level 0 mean and stdev from frequency and pulse width moments
        pause_mean = 1 / freq_mean - width_mean
        pause_stddev = math.sqrt(freq_stddev**2 - width_stddev**2) / 2

        # make noise pulses
        self.signal = []
        noise = self.signal
        last_pause_end = 0
        while True:
            # not really true gauss: negative branch reflected over positive and
            # zero value not allowed.
            width = abs(int(random.gauss(width_mean,width_stddev))) + 1
            pause = abs(int(random.gauss(pause_mean,pause_stddev))) + 1
            if last_pause_end + width + pause <= time_end:
                noise.append(last_pause_end)
                noise.append(last_pause_end + width)
                last_pause_end += width + pause
            else:
                break


    def __eq__(self,signal):
        """ Signal objetcs equality test. """

        if self.__dict__ == signal.__dict__:
            return True
        else:
            try:
                print '1 ****'
                print self
                print '2 ****'
                print signal
            except:
                pass


    def __and__(self,signal):
        """ Compute the logic and of twoi given signal object: *self* and
        *signal*. Returns a signal object with the and of the two input
        signals. """

        # create signal object for and storage
        and_obj = Signal()
        sig_and = and_obj.signal

        # simplify var access
        sig_a = self.signal
        len_a = self.length
        sig_b = signal.signal
        len_b = signal.length
        off_ba = signal.time_offset - self.time_offset

        # status vars of a two input logic and: inputs a and b, output a_and_b.
        a = 0
        b = 0
        a_and_b = 0

        # get all edges, one at a time, from the two lists as sorted by
        # ascending time, do it until the end of one of the two lists is
        # reached.
        i = 0
        j = 0
        while i < len_a and j < len_b:
            # get the next edge in time. If the next edge makes a change to the
            # and output, append it to the output anded pulses and update and
            # logic output (a_and_b).
            # Always update and logic inputs (a,b) and list pointers (i,j)
            if sig_a[i] < sig_b[j] + off_ba:
                a = not (i & 1) ^ self.initial_value
                if a_and_b != (a and b):
                    sig_and.append(sig_a[i])
                    a_and_b = a and b
                i += 1
            elif sig_a[i] > sig_b[j] + off_ba:
                b = not (j & 1) ^ signal.initial_value
                if a_and_b != (a and b):
                    sig_and.append(sig_b[j] + off_ba)
                    a_and_b = a and b
                j += 1
            else:
                a = not (i & 1) ^ self.initial_value
                b = not (j & 1) ^ signal.initial_value
                if a_and_b != (a and b):
                    sig_and.append(sig_a[i])
                    a_and_b = a and b
                i += 1
                j += 1

        # set initial value, length and time offset
        and_obj.initial_value = self.initial_value and signal.initial_value
        and_obj.length = len(sig_and)
        and_obj.time_offset = self.time_offset

        return and_obj


    def __or__(self,signal):
        """ Compute the logic or of two given signal object: *self* and
        *signal*. Returns a signal object with the or of the two input
        signals. """

        # create signal object for and storage
        or_obj = Signal()
        sig_or = or_obj.signal

        # simplify var access
        sig_a = self.signal
        len_a = self.length
        sig_b = signal.signal
        len_b = signal.length
        off_ba = signal.time_offset - self.time_offset

        # status vars of a two input logic or: inputs a and b, output a_or_b.
        a = 0
        b = 0
        a_or_b = 0

        # get all edges, one at a time, from the two lists as sorted by
        # ascending time, do it until the end of one of the two lists is
        # reached.
        i = 0
        j = 0
        while i < len_a and j < len_b:
            # get the next edge in time. If the next edge makes a change to the
            # or output, append it to the output ored pulses and update or logic
            # output (a_or_b).
            # Always update or logic inputs (a,b) and list pointers (i,j)
            if sig_a[i] < sig_b[j] + off_ba:
                a = not (i & 1) ^ self.initial_value
                if a_or_b != (a | b):
                    sig_or.append(sig_a[i])
                    a_or_b = (a | b)
                i += 1
            elif sig_a[i] > sig_b[j] + off_ba:
                b = not (j & 1) ^ signal.initial_value
                if a_or_b != (a | b):
                    sig_or.append(sig_b[j] + off_ba)
                    a_or_b = (a | b)
                j += 1
            else:
                a = not (i & 1) ^ self.initial_value
                b = not (j & 1) ^ signal.initial_value
                if a_or_b != (a | b):
                    sig_or.append(sig_a[i])
                    a_or_b = (a | b)
                i += 1
                j += 1

        # if one of sig_a or sig_b is exausted, the remaining part of
        # the other is appended unchanged to the result: equivalent to oring
        # it with zero.
        if i >= len_a and j < len_b:
            sig_or.extend([change + off_ba for change in sig_b[j:]])
        if i < len_a and j >= len_b:
            sig_or.extend(sig_a[i:])

        # set initial value, length and time offset
        or_obj.initial_value = self.initial_value or signal.initial_value
        or_obj.length = len(sig_or)
        or_obj.time_offset = self.time_offset

        return or_obj


    def __xor__(self,signal):
        """ Compute the logic xor of two given signal objects: *self* and
        *signal*. Returns a signal object with the xor of the two input
        signals. """

        # create signal object for xor storage
        xor_obj = Signal()
        sig_xor = xor_obj.signal

        # xor is the union of pulse edges sorted by time
        sig_xor += self.signal + signal.signal
        sig_xor.sort()

        # simultaneous edges cancel each other, so, if any, remove them.
        i = 0
        while i < len(sig_xor) - 1:
            if not sig_xor[i] - sig_xor[i + 1]:
                del sig_xor[i]
                del sig_xor[i]
            else:
                i += 1

        # set initial value, length and time offset
        xor_obj.initial_value = self.initial_value ^ signal.initial_value
        xor_obj.length = len(sig_xor)
        xor_obj.time_offset = self.time_offset

        return xor_obj


    def __invert__(self):
        """ Compute the logic not of given *self* signal object.
        Returns a signal object that is a copy of the input signal with
        initial value inverted. """

        not_obj = self.clone()
        not_obj.initial_value = not self.initial_value 

        return not_obj


    def integral(self):
        """ Returns the integral (int) of signal: the summation of all periods
        in which the signal is at one level. """

        integral = 0
        signal = self.signal
        for i in range(0,len(signal),2):
            integral += signal[i + 1] - signal[i]

        return integral

#### END
