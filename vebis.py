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
    timing of signal changes (signal edges). This representation is useful
    when the signal has a low rate of change with respect to the sampling
    period. In this case, the representation is very compact in memory.
    The first element of signal sequence has always change time = 0. The
    sequence can be shifted in time by specifying a time offset. The signal
    level before the first change is specified by a initial value. The
    signal level after the last change is equal to initial value, if changes
    are even, otherwise is inverted. """

    # a test signal with a sequence of primes as edges timing
    TEST_EDGES = [0,1,2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61]


    def __init__(self,edges=[],initial_value=0,time_offset=0,
            time_scale=1):

        # sequence of signal changes times
        if edges:
            self.edges = edges
        else:
            self.edges = []
        # signal level before the first change
        self.initial_value = initial_value
        # number of signal changes
        try:
            self.length = len(edges)
        except:
            self.length = 0
        # time offset affecting all signal changes
        self.time_offset = time_offset
        # time scale of changes time (1=1s)
        self.time_scale = time_scale


    def __str__(self):
       
        descr = '%s\n' % object.__str__(self)
        descr += '  edges: %s\n' % self.edges
        descr += '  initial value: %d\n' % self.initial_value
        descr += '  length: %d\n' % self.length
        descr += '  time offset: %d\n' % self.time_offset
        descr += '  time scale: %d' % self.time_scale

        return descr


    def test(self):
        """ Fill current signal object with a test signal. Previous signal
        data is destroyed. """

        # fill current signal changes and its length attribute
        self.edges = self.TEST_EDGES
        self.length = len(self.TEST_EDGES)


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
        edges = self.edges
        length = self.length

        # reversal time adjusting constant
        time_adjust = edges[-1]

        # reverse edges times
        for i in range(length-1,-1,-1):
            edges[i] = time_adjust - edges[i]

        # edges sequence needs to have ascending times
        edges.sort()


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


    def noise(self,time_start,time_end,freq_mean=1,freq_stddev=1,
            width_mean=0.1,width_stddev=0.1,random_initial_value=True):
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
        self.edges = []
        noise = self.edges
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

        # set a random intial value and edges sequence length
        self.initial_value = pause & 1
        self.length = len(noise)


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


    def _bioper(self,other,operator):
        """ Compute the logic and of twoi given signal object: *self* and
        *signal*. Returns a signal object with the and of the two input
        signals. """

        # create signal object for and storage
        out_obj = Signal()
        ed_out = out_obj.edges

        # simplify var access
        ed_a = self.edges
        len_a = self.length
        ed_b = other.edges
        len_b = other.length
        off_ba = other.time_offset - self.time_offset

        # initial status vars of a two input logic: inputs a and b, output.
        in_a = self.initial_value
        in_b = other.initial_value
        out = operator(in_a,in_b)
        out_obj.initial_value = out

        # get all edges, one at a time, from the two lists as sorted by
        # ascending time, do it until the end of one of the two lists is
        # reached.
        i = 0
        j = 0
        while i < len_a and j < len_b:
            # get the next edge in time. If the next edge makes a change to the
            # and output, append it to the output anded pulses and update and
            # logic output (a_and_b).
            # Always update logic inputs (a,b) and list pointers (i,j)
            if ed_a[i] < ed_b[j] + off_ba:
                in_a = not in_a
                if out != operator(in_a,in_b):
                    ed_out.append(ed_a[i])
                    out = operator(in_a,in_b)
                i += 1
            elif ed_a[i] > ed_b[j] + off_ba:
                in_b = not in_b
                if out != operator(in_a,in_b):
                    ed_out.append(ed_b[j] + off_ba)
                    out = operator(in_a,in_b)
                j += 1
            else:
                in_a = not in_a
                in_b = not in_b
                if out != operator(in_a,in_b):
                    ed_out.append(ed_a[i])
                    out = operator(in_a,in_b)
                i += 1
                j += 1

        # if one of ed_a or ed_b is exausted, the remaining part of
        # the other is appended unchanged to the result: equivalent to oring
        # it with zero.
        if i >= len_a and j < len_b:
            if operator(in_a,0) != operator(in_a,1):
                ed_out.extend([change + off_ba for change in ed_b[j:]])
        if i < len_a and j >= len_b:
            if operator(in_b,0) != operator(in_b,1):
                ed_out.extend(ed_a[i:])

        # set initial value, length and time offset
        out_obj.length = len(ed_out)
        out_obj.time_offset = self.time_offset

        return out_obj


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
        xor_obj = Signal()
        ed_xor = xor_obj.edges

        # xor is the union of pulse edges sorted by time
        ed_xor += self.edges + other.edges
        ed_xor.sort()

        # simultaneous edges cancel each other, so, if any, remove them.
        i = 0
        while i < len(ed_xor) - 1:
            if not ed_xor[i] - ed_xor[i + 1]:
                del ed_xor[i]
                del ed_xor[i]
            else:
                i += 1

        # set initial value, length and time offset
        xor_obj.initial_value = self.initial_value ^ other.initial_value
        xor_obj.length = len(ed_xor)
        xor_obj.time_offset = self.time_offset

        return xor_obj


    def __invert__(self):
        """ Compute the logic not of given *self* signal object.
        Returns a signal object that is a copy of the input signal with
        initial value inverted. """

        not_obj = self.clone()
        not_obj.initial_value = not self.initial_value 

        return not_obj


    def integral(self,level=1):
        """ Returns the integral (int) of signal: the summation of all periods
        in which the signal is at the level specified by *level* argument. The
        summation is operated on the signal domain only: levels at 1 before the
        first signal edge and after the last edge are ignored. """

        # simplify var access
        edges = self.edges
        length = self.length
        level = self.initial_value ^ (not level)

        # do level 1 summation between first and last signal edges
        integral = 0
        for i in range(level,length,2):
            try:
                integral += edges[i + 1] - edges[i]
            except:
                pass

        return integral


    def correlation(self,other):
        """ Returns the unormalized correlation function of two signals
        (*self* and *other*). """

        # simplify variables access
        signal_a = self.clone()
        signal_b = other.clone()
        edges_a = signal_a.edges
        edges_b = signal_b.edges
        length_a = signal_a.length
        length_b = signal_b.length
        off_a = signal_a.time_offset
        off_b = signal_b.time_offset

        # take the first edge of signal B as origin. Keep signal B fixed in
        # time and slide signal A. To start, shift A last edge on the first
        # edge of B.
        shift = edges_b[0] + off_b - edges_a[-1] - off_a
        print 'shift=',shift
        for i in range(length_a):
            edges_a[i] += shift

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

        from matplotlib.pyplot import step

        # generate signal values
        values = [self.initial_value]
        for i in range(1,self.length):
            values += [not values[-1]]

        if args:
            step(self.edges,values,args)
        elif kargs:
            step(self.edges,values,kargs)
        elif args and kargs:
            step(self.edges,values,args,kargs)
        else:
            step(self.edges,values)

#### END
