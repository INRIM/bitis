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
# .-


#### import required modules

import copy             # object copy support
import math             # mathematical support
import random           # random generation


#### classes

class Signal:
    """ Implements the concept of "Vectorial Binary Signal", a memory
    representation of a binary signal by a vector or list filled with the
    time of signal changes (signal edges). This representation is useful
    when the signal has a low rate of change with respect to the sampling
    period. In this case, the representation is very compact in memory.
    The first element of signal sequence has always change time = 0. The
    sequence can be shifted in time by specifying a time offset. The signal
    level before the first change is specified by a initial value. The
    signal level after the last change is equal to initial value, if changes
    are even, otherwise is inverted. """

    # a test signal with a sequence of primes as changes timing
    TEST_TIMES = [-1,0,1,2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,62]


    def __init__(self,times=None,slevel=0,tscale=1):

        # sequence of signal (start,changes,end) times
        if times:
            self.times = times
        # undefined signal: no start, no change, no end times.
        else:
            self.times = []
        # signal level before the first change
        self.slevel = slevel
        # time scale of changes time (1=1s)
        self.tscale = tscale


    def __str__(self):
       
        descr = '%s\n' % object.__str__(self)
        descr += '  times: %s\n' % self.times
        descr += '  start level: %d\n' % self.slevel
        descr += '  time scale: %d' % self.tscale

        return descr


    def test(self):
        """ Fill current signal object with a test signal. Previous signal
        times are destroyed. Start level and time scale are preserved. """

        self.times = self.TEST_TIMES


    def clone(self):
        """ Returns a copy with the same attributes/values of current the
        instance. """

        return copy.deepcopy(self)


    def shift(self,offset):
        """ Get/Set the time offset (s) for all signal changes. If
        *offset* is not specified, returns the time offset value (int)i
        stored in the signal object. Otherwise, set it. """

        for i in range(len(self.times)):
                self.times[i] += offset


    def reverse(self):
        """ Reverse the signal edge sequence: last change becomes the first
        and viceversa. Time intervals between all changes are preserved.
        Returns the same input signal object with the updated times. """

        # set start level: if times number is odd, must be inverted.
        if len(self.times) & 1:
            self.slevel = not self.slevel

        # reverse change times, not first and last times (start and end).
        for i in range(len(self.times)-2,0,-1):
            self.times[i] = self.times[-1] - self.times[i]

        # edges sequence needs to have ascending times
        self.times.sort()


    def jitter(self,jitter_stddev=0):
        """ Add a gaussian jitter to *signal* with the given standard deviation
        *jitter_stddev* (s) and zero mean. The first and last signal edges are
        unchanged. The jitter is added to the current signal istance. """

        # convert to proper time scale
        jitter_stddev *= self.time_scale

        # simplify access
        edges = self.edges
        length = self.length

        # add jitter to signal edges
        for edge in range(1,length-1):
            # if current edge has room to be moved forward or back, add jitter.
            if edges[i+1] - edges[i-1] > 2:
                edges[i] += int(random.gauss(0.0,jitter_stddev))
                # limit jitter range inside prevoius and next edges
                if edges[i] <= edges[i-1]:
                    edges[i] = edges[i-1] + 1
                elif edges[i] >= edges[i+1]:
                    edges[i] = edges[i+1] - 1


    def noise(self,start,end,freq_mean=1,freq_stddev=1,
            width_mean=1,width_stddev=1,random_initial_value=True):
        """ Fill current signal object with disturbing pulses. Pulses time
        domain extends from *start* to *end*. Pulses
        frequency and width follow a gaussian distribution: *freq_mean* and
        *freq_stddev* are the given mean and standard deviation of frequency
        in hertz, *width_mean* and *width_stddev* are the given mean and
        standard deviation of the pulse width in seconds (1 level).
        Previous signal data is destroyed. """

        # level 0 mean and stdev from frequency and pulse width moments
        pause_mean = 1 / freq_mean - width_mean
        pause_stddev = math.sqrt(freq_stddev**2 - width_stddev**2) / 2

        # set start and a random start level
        self.times = [start]
        self.slevel = random.randint(0,1)

        # insert first pause interval end
        last_pause_end = \
                abs(int(random.gauss(pause_mean,pause_stddev))) + 1 + start
        if last_pause_end > end:
            self.times.append(end)
            return

        # make noise pulses
        while True:
            # not really true gauss: negative branch reflected over positive and
            # zero value not allowed.
            width = abs(int(random.gauss(width_mean,width_stddev))) + 1
            pause = abs(int(random.gauss(pause_mean,pause_stddev))) + 1
            if last_pause_end + width + pause > end:
                break
            self.times.append(last_pause_end)
            self.times.append(last_pause_end + width)
            last_pause_end = last_pause_end + width + pause


    def __eq__(self,other):
        """ Signal objetcs equality test. """

        if self.__dict__ == other.__dict__:
            return True
        else:
            try:
                print '1 ****'
                print self
                print '2 ****'
                print other
            except:
                pass
            return False


    def _intersect(self,other):
        """ """

        # start and end times of signal A and B intersection
        start = max(self.times[0],other.times[0])
        end = min(self.times[-1],other.times[-1])

        # if no intersection, return none
        if start >= end:
            return None

        # find index of first change after start
        
        for ia_start in range(len(self.times)):
            if self.times[ia_start] > start:
                break

        for ib_start in range(len(other.times)):
            if other.times[ib_start] > start:
                break

        # find index of last change before end

        for ia_end in range(-1,-len(self.times)-1,-1):
            if self.times[ia_end] < end:
                ia_end += len(self.times)
                break

        for ib_end in range(-1,-len(other.times)-1,-1):
            if other.times[ib_end] < end:
                ib_end += len(other.times)
                break

        # compute level before first change after start
        slevel_a = self.slevel ^ (~ia_start & 1)
        slevel_b = other.slevel ^ (~ib_start & 1)

        return start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b


    def _bioper(self,other,operator):
        """ Compute the logic and of twoi given signal object: *self* and
        *signal*. Returns a signal object with the and of the two input
        signals. """

        # if one or both operand is none, return none as result.
        if not self or not other:
            return None

        # create output signal object
        out_sig = Signal()

        # compute A and B time intersection paramenters.
        # If no intersection, return none.
        intersection = self._intersect(other)
        if not intersection:
            return None
        start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b = \
            intersection

        # initial status vars of a two input logic: inputs a and b, output.
        in_a = slevel_a
        in_b = slevel_b
        out_sig.slevel = operator(in_a,in_b)
        out = out_sig.slevel

        # get all edges, one at a time, from the two lists as sorted by
        # ascending time, do it until the end of one of the two lists is
        # reached.
        out_sig.times = [start]
        ia = ia_start
        ib = ib_start
        while ia <= ia_end and ib <= ib_end:
            # get the next edge in time. If the next edge makes a change to the
            # and output, append it to the output anded pulses and update and
            # logic output (a_and_b).
            # Always update logic inputs (a,b) and list pointers (i,j)
            if self.times[ia] < other.times[ib]:
                in_a = not in_a
                if out != operator(in_a,in_b):
                    out_sig.times.append(self.times[ia])
                    out = not out
                ia = ia + 1
            elif self.times[ia] > other.times[ib]:
                in_b = not in_b
                if out != operator(in_a,in_b):
                    out_sig.times.append(other.times[ib])
                    out = not out
                ib = ib + 1
            else:
                in_a = not in_a
                in_b = not in_b
                if out != operator(in_a,in_b):
                    out_sig.times.append(self.times[ia])
                    out = not out
                ia = ia + 1
                ib = ib + 1

        # if one of A or B is exausted, the remaining part of
        # the other is appended unchanged to the result: equivalent to oring
        # it with zero.
        if ia > ia_end and ib <= ib_end:
            in_a = self.slevel ^ ((ia - 1) & 1)
            if operator(in_a,0) != operator(in_a,1):
                out_sig.times.extend(other.times[ib:ib_end + 1])
        elif ia <= ia_end and ib > ib_end:
            in_b = other.slevel ^ ((ib - 1) & 1)
            if operator(in_b,0) != operator(in_b,1):
                out_sig.times.extend(self.times[ia:ia_end + 1])
        out_sig.times.append(end)

        return out_sig


    def __and__(self,other):
        """ Compute the logic and of twoi given signal object: *self* and
        *signal*. Returns a signal object with the and of the two input
        signals. """

        return self._bioper(other,lambda a,b: a and b)


    def __or__(self,other):
        """ Compute the logic or of two given signal object: *self* and
        *signal*. Returns a signal object with the or of the two input
        signals. """

        return self._bioper(other,lambda a,b: a or b)


    def __xor__(self,other):
        """ Compute the logic xor of two given signal objects: *self* and
        *signal*. Returns a signal object with the xor of the two input
        signals. """

        # if one or both operand is none, return none as result.
        if not self or not other:
            return None

        # create signal object for xor storage
        xor_sig = Signal()

        # compute A and B time intersection paramenters.
        # If no intersection, return none.
        intersection = self._intersect(other)
        if not intersection:
            return None
        start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b = \
            intersection

        # set start level
        xor_sig.slevel = slevel_a ^ slevel_b

        # xor is the union of pulse edges sorted by time
        xor_sig.times = [start] + self.times[ia_start:ia_end+1] \
                + other.times[ib_start:ib_end+1] + [end]
        xor_sig.times.sort()

        # simultaneous edges cancel each other, so, if any, remove them.
        i = 1 
        while i < len(xor_sig.times) - 2:
            if not xor_sig.times[i] - xor_sig.times[i + 1]:
                del xor_sig.times[i]
                del xor_sig.times[i]
            else:
                i += 1

        # the last couple do not cancel each other: one value must survive,
        # it is the end time.
        if not xor_sig.times[-2] - xor_sig.times[-1]:
            del xor_sig.times[-1]

        return xor_sig


    def __invert__(self):
        """ Compute the logic not of given *self* signal object.
        Returns a signal object that is a copy of the input signal with
        start level inverted. """

        not_sig = self.clone()
        not_sig.slevel = not self.slevel

        return not_sig


    def integral(self,level=1,normalize=False):
        """ Returns the integral (int) of signal: the summation of all periods
        in which the signal is at the level specified by *level* argument. The
        summation is operated on the signal domain only: levels at 1 before the
        first signal edge and after the last edge are ignored. """

        # do summation between first and last signal changes
        changes_int = 0
        for i in range(1,len(self.times),2):
            try:
                changes_int = changes_int + self.times[i + 1] - self.times[i]
            except:
                pass

        # return summation of level=0 or =1 as requested by level argument
        if level ^ self.slevel:
            integral = changes_int
        else:
            integral = self.times[-1] - self.times[0] - changes_int

        # return normalized if requested by normalized argument
        if normalize:
            integral = float(integral) / (self.times[-1] - self.times[0])

        return integral


    def correlation(self,other,normalize=False):
        """ Returns the unormalized correlation function of two signals
        (*self* and *other*). """

        # simplify variables access
        sig_a = self.clone()
        sig_b = other.clone()

        # take the first edge of signal B as origin. Keep signal B fixed in
        # time and slide signal A. To start, shift A end on the first change
        # of B.
        shift = sig_b.times[0] - sig_a.times[-1] + 1
        print 'shift=',shift
        for i in range(len(sig_a.times)):
            sig_a.times[i] = sig_a.times[i] + shift

        # detect the values of the phasing variable corresponding to
        # the vertex of the correlation function
        phi = sig_b.times[:]
        print 'phi=',phi
        for i in range(len(sig_a.times)-2,-1,-1):
            off_aa = sig_a.times[i + 1] - sig_a.times[i]
            print 'off_aa=',off_aa
            for j in range(len(sig_b.times)):
                sig_b.times[j] += off_aa
            phi += sig_b.times[:]
            print 'phi=',phi
        phi.sort()
        del phi[-1]

        # keep only unique phase values
        k = 0
        while k < len(phi) - 1:
            if not phi[k] - phi[k + 1]:
                del phi[k]
            else:
                k += 1
        print 'phi=',phi

        # set proper origin to phi values
        adjust = shift - phi[0]
        for k in range(len(phi)):
            phi[k] = phi[k] + adjust
        print 'phi=',phi

        # reset signal B edges to the original time values
        sig_b.times = other.times[:]

        # compute correlation function at previuosly computed phase values

        # correlation among signal A and B
        corr = []
        last_ph = phi[0]
        for ph in phi[:-1]:
            print 'ph=',ph
            dph = ph - last_ph
            last_ph = ph
            # apply phase to signal A
            for i in range(len(sig_a.times)):
                sig_a.times[i] = sig_a.times[i] + dph
            print 'sig_a.times=',sig_a.times
            print 'sig_b.times=',sig_b.times

            # correlation among signal A and B
            if normalize:
                corr += [(sig_a ^ other).integral(0,normalize) * 2 - 1]
            else:
                corr += [(sig_a ^ other).integral(0,normalize=False)]
            print 'xor=',sig_a ^ sig_b
            print 'corr=',corr

        return corr, phi[:-1]



    def plot(self,*args,**kargs):
        """ Plot signal as square wave. """

        from matplotlib.pyplot import plot

        # generate signal levels
        levels = [self.slevel]
        for i in range(1,len(self.times)):
            levels += [not levels[-1]]

        # set proper draw style for square waves
        if not kargs:
            kargs = {}
        kargs.update({'drawstyle':'steps-post'})

        # if there are given args, pass them
        if args:
            plot(self.times,levels,*args,**kargs)
        else:
            plot(self.times,levels,**kargs)

#### END
