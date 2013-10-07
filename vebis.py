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
    TEST_TIMES = (-1,62,[0,1,2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61])


    def __init__(self,times=None,slevel=0,tscale=1):

        # sequence of signal (start,end,changes) times
        if times:
            self.stime = times[0]
            self.etime = times[1]
            self.ctimes = times[2]
            # check for valid start and end times
            if self.stime > self.ctimes[0]:
                raise Exception('start time after first change time.')
            if self.etime < self.ctimes[-1]:
                raise Exception('end time before last change time.')
        # undefined signal: no start/end times, no change times.
        else:
            self.stime = None
            self.etime = None
            self.ctimes = []
        # signal level before the first change
        self.slevel = slevel
        # time scale of changes time (1=1s)
        self.tscale = tscale


    def __str__(self):
       
        descr = '%s\n' % object.__str__(self)
        descr += '  start time: %s\n' % self.stime
        descr += '  end time: %s\n' % self.etime
        descr += '  change times: %s\n' % self.ctimes
        descr += '  start level: %d\n' % self.slevel
        descr += '  time scale: %d' % self.tscale

        return descr


    def test(self):
        """ Fill current signal object with a test signal. Previous signal
        times are destroyed. Start level and time scale are preserved. """

        self.stime = self.TEST_TIMES[0]
        self.etime = self.TEST_TIMES[1]
        self.ctimes = self.TEST_TIMES[2]


    def clone(self):
        """ Returns a copy with the same attributes/values of current the
        instance. """

        return copy.deepcopy(self)


    def shift(self,offset):
        """ Get/Set the time offset (s) for all signal changes. If
        *offset* is not specified, returns the time offset value (int)i
        stored in the signal object. Otherwise, set it. """

        self.stime += offset
        self.etime += offset
        for i in range(len(self.ctimes)):
                self.ctimes[i] += offset


    def reverse(self):
        """ Reverse the signal edge sequence: last edge becomes the first
        and viceversa.Time intervals between all edges are preserved.
        Returns the same input signal object with the updated signal. """

        # reverse edges times
        for i in range(len(self.ctimes)-1,-1,-1):
            self.ctimes[i] = self.etime - self.ctimes[i]

        # edges sequence needs to have ascending times
        self.ctimes.sort()


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

        # set start, end and a random start level
        self.stime = start
        self.etime = end
        self.slevel = int(random.gauss(width_mean,width_stddev)) & 1

        # insert first pause interval end
        last_pause_end = \
                abs(int(random.gauss(pause_mean,pause_stddev))) + 1 + start
        if last_pause_end > end:
            self.ctimes = []
            return
        self.ctimes = [last_pause_end]

        # make noise pulses
        while True:
            # not really true gauss: negative branch reflected over positive and
            # zero value not allowed.
            width = abs(int(random.gauss(width_mean,width_stddev))) + 1
            pause = abs(int(random.gauss(pause_mean,pause_stddev))) + 1
            if last_pause_end + width + pause > end:
                break
            self.ctimes.append(last_pause_end + pause)
            self.ctimes.append(last_pause_end + pause + width)
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
        start = max(self.stime,other.stime)
        end = min(self.etime,other.etime)

        # if no intersection, return none
        if start >= end:
            return None

        # find index of first change after start
        
        for ia_start in range(len(self.ctimes)):
            if self.ctimes[ia_start] >= start:
                break
        else:
            ia_start = None

        for ib_start in range(len(other.ctimes)):
            if other.ctimes[ib_start] >= start:
                break
        else:
            ib_start = None

        # find index of last change before end

        for ia_end in range(-1,-len(self.ctimes)-1,-1):
            if self.ctimes[ia_end] <= end:
                ia_end += len(self.ctimes)
                break
        else:
            ia_end = None

        for ib_end in range(-1,-len(other.ctimes)-1,-1):
            if other.ctimes[ib_end] <= end:
                ib_end += len(other.ctimes)
                break
        else:
            ib_end = None

        # compute level before first change after start
        slevel_a = self.slevel ^ (bool(ia_start) & 1)
        slevel_b = other.slevel ^ (bool(ib_start) & 1)

        return start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b


    def _bioper(self,other,operator):
        """ Compute the logic and of twoi given signal object: *self* and
        *signal*. Returns a signal object with the and of the two input
        signals. """

        # create output signal object
        out_sig = Signal()

        # compute A and B time intersection paramenters
        start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b = \
                self._intersect(other)

        # set start and end
        out_sig.stime = start
        out_sig.etime = end

        # initial status vars of a two input logic: inputs a and b, output.
        in_a = slevel_a
        in_b = slevel_b
        out = operator(in_a,in_b)
        out_sig.slevel = out

        # get all edges, one at a time, from the two lists as sorted by
        # ascending time, do it until the end of one of the two lists is
        # reached.
        ia = ia_start
        ib = ib_start
        while ia <= ia_end and ib <= ib_end:
            # get the next edge in time. If the next edge makes a change to the
            # and output, append it to the output anded pulses and update and
            # logic output (a_and_b).
            # Always update logic inputs (a,b) and list pointers (i,j)
            if self.ctimes[ia] < other.ctimes[ib]:
                in_a = not in_a
                if out != operator(in_a,in_b):
                    out_sig.ctimes.append(self.ctimes[ia])
                    out = operator(in_a,in_b)
                ia = ia + 1
            elif self.ctimes[ia] > other.ctimes[ib]:
                in_b = not in_b
                if out != operator(in_a,in_b):
                    out_sig.ctimes.append(other.ctimes[ib])
                    out = operator(in_a,in_b)
                ib = ib + 1
            else:
                in_a = not in_a
                in_b = not in_b
                if out != operator(in_a,in_b):
                    out_sig.ctimes.append(self.ctimes[ia])
                    out = operator(in_a,in_b)
                ia = ia + 1
                ib = ib + 1

        # if one of A or B is exausted, the remaining part of
        # the other is appended unchanged to the result: equivalent to oring
        # it with zero.
        if ia >= ia_end and ib < ib_end:
            if operator(in_a,0) != operator(in_a,1):
                out_sig.ctimes.extend(other.ctimes[ib:])
        if ia < ia_end and ib >= ib_end:
            if operator(in_b,0) != operator(in_b,1):
                out_sig.ctimes.extend(self.ctimes[ia:])

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

        # create signal object for xor storage
        xor_sig = Signal()

        # compute A and B time intersection paramenters
        start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b = \
                self._intersect(other)

        # set start, end and start level
        xor_sig.stime = start
        xor_sig.etime = end
        xor_sig.slevel = slevel_a ^ slevel_b

        # xor is the union of pulse edges sorted by time
        xor_sig.ctimes = self.ctimes[ia_start:ia_end+1] \
                + other.ctimes[ib_start:ib_end+1]
        xor_sig.ctimes.sort()

        # simultaneous edges cancel each other, so, if any, remove them.
        i = 0
        while i < len(xor_sig.ctimes) - 1:
            if not xor_sig.ctimes[i] - xor_sig.ctimes[i + 1]:
                del xor_sig.ctimes[i]
                del xor_sig.ctimes[i]
            else:
                i += 1

        return xor_sig


    def __invert__(self):
        """ Compute the logic not of given *self* signal object.
        Returns a signal object that is a copy of the input signal with
        start level inverted. """

        not_sig = self.clone()
        not_sig.slevel = not self. slevel

        return not_sig


    def integral(self,level=1,mean=False):
        """ Returns the integral (int) of signal: the summation of all periods
        in which the signal is at the level specified by *level* argument. The
        summation is operated on the signal domain only: levels at 1 before the
        first signal edge and after the last edge are ignored. """

        # do summation between first and last signal changes
        changes_int = 0
        for i in range(0,len(self.ctimes),2):
            try:
                changes_int = changes_int + self.ctimes[i + 1] - self.ctimes[i]
            except:
                pass

        # return summation of level=0 or =1 as requested by level argument
        if level ^ self.slevel:
            integral = changes_int
        else:
            integral = self.etime - self.stime - changes_int

        # return mean if requested by mean argument
        if mean:
            integral = float(integral) / (self.etime - self.stime)

        return integral


    def correlation(self,other):
        """ Returns the unormalized correlation function of two signals
        (*self* and *other*). """

        # simplify variables access
        sig_a = self.clone()
        sig_b = other.clone()

        # take the first edge of signal B as origin. Keep signal B fixed in
        # time and slide signal A. To start, shift A last edge on the first
        # edge of B.
        shift = sig_b.stime - sig_a.etime
        print 'shift=',shift
        for i in range(len(sig_a.ctimes)):
            sig_a.ctimes[i] = sig_a.ctimes[i] + shift

        # detect the values of the phasing variable corresponding to
        # the vertex of the correlation function
        phi = edges_b[:]
        print 'phi=',phi
        for i in range(length_a-2,-1,-1):
            off_aa = edges_a[i + 1] - edges_a[i]
            print 'off_aa=',off_aa
            for j in range(length_b):
                edges_b[j] += off_aa
            phi += edges_b[:]
            print 'phi=',phi
        phi.sort()

        # keep only unique phase values
        k = 0
        while k < len(phi) - 1:
            if not phi[k] - phi[k + 1]:
                del phi[k]
            else:
                k += 1
        print 'phi=',phi

        # reset signal B edges to the original time values
        edges_b = other.edges[:]

        # compute correlation function at previuosly computed phase values
        signal_b.edges = edges_b
        corr = []
        for ph in phi:
            print 'ph=',ph
            # apply phase to signal A
            for i in range(length_a):
                edges_a[i] += ph
            print 'edges_a=',edges_a
            print 'edges_b=',edges_b

            # correlation among signal A and B
            signal_a.edges = edges_a
            corr += [(signal_a ^ signal_b).integral(0)]
            print 'xor=',signal_a ^ signal_b
            print 'corr=',corr

        return corr, phi


    def plot(self,*args,**kargs):
        """ Plot signal as square wave. """

        from matplotlib.pyplot import plot

        # generate signal levels and times
        levels = [self.slevel]
        for i in range(len(self.ctimes)):
            levels += [not levels[-1]]
        levels += [levels[-1]]
        times = [self.stime] + self.ctimes + [self.etime]

        # set proper draw style for square waves
        if not kargs:
            kargs = {}
        kargs.update({'drawstyle':'steps-post'})

        # if there are given args, pass them
        if args:
            plot(times,levels,*args,**kargs)
        else:
            plot(times,levels,**kargs)

#### END
