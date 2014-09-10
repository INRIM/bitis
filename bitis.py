#.!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Processing Library
# .title      : Bitis main module
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	26-Sep-2013
# .copyright  :	(c) 2013-2014 Fabrizio Pollastri
# .license    : GNU General Public License (see below)
#
# This file is part of "Bitis, Binary Timed Signal Processig Library".
#
# Bitis is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Bitis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.
#
# .-


### import required modules

import copy             # object copy support
import math             # mathematical support
import random           # random generation
import sys              # sys constants


# define global variables

__version__ = '0.9.0'
__author__ = 'Fabrizio Pollastri <f.pollastri@inrim.it>'


#### classes

class Signal:
    """
    Implements the concept of "Binary Timed Signal": a memory
    representation of a binary signal as sequence of the times of
    signal edges (signal changes).
    *start* sets the signal start time.
    *edges* can be used to initialize the signal edges sequence, it must
    be a list of times (integers or floats). May be empty.
    The signal level before the first change is specified by *slevel*.
    Also a time scale factor can be specified by *tscale*, at present
    not used.
    """

    # a test signal with a sequence of primes as edges timing
    TEST_START = -1
    TEST_EDGES = [0,1,2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61]
    TEST_END = 62


    def __init__(self,start=None,edges=None,end=None,slevel=0,tscale=1):

        # signal start time
        self.start = start
        # sequence of signal change times
        if edges is None:
            self.edges = []
        else:
           self.edges = edges
        # signal end time
        self.end = end
        # signal level before the first change
        self.slevel = slevel
        # time scale of edges time (1=1s)
        self.tscale = tscale


    def __str__(self):
       
        descr = '%s\n' % object.__str__(self)
        descr += '  start: %s\n' % self.start
        descr += '  edges: %s\n' % self.edges
        descr += '  end: %s\n' % self.end
        descr += '  start level: %d\n' % self.slevel
        descr += '  time scale: %d' % self.tscale

        return descr


    def level(self,time,tpos=0):
        """ Return the logic level and the number of edges of a signal object at
        a given time (*time*) and a given edge position where to start searching
        (*tpos*). The edge position is the number of signal edges before *time*.
        When *time* is equal to an edge time that edge is considered before
        *time*.
        *time* must be in the signal time domain, otherwise None is returned.
        *tpos* must point to an edge before *time*. """

        try:
            while time > self.edges[tpos]:
                tpos += 1
        except:
            if time > self.end:
                return None, None
            else:
                return (len(self) - 1) & 1 ^ self.slevel, len(self)
        tpos -= 1
        return tpos & 1 ^ self.slevel, tpos


    def test(self):
        """ Fill signal object with a test signal. Previous signal
        times are destroyed. Start level and time scale are preserved. """

        self.start = self.TEST_START
        self.edges = self.TEST_EDGES
        self.end = self.TEST_END


    def clone(self):
        """ Return a deep copy with the same attributes/values of signal
        object. """

        return copy.deepcopy(self)


    def clone_into(self,other):
        """ Full copy of signal object into *other*. Each other attribute is
        assigned a deep copy of the value of the same attribute in signal
        object. Return *other*. """

        other.start = self.start
        other.edges = self.edges[:]
        other.end = self.end
        other.slevel = self.slevel
        other.tscale = self.tscale


    def elapse(self):
        """ Ruturn the signal elapse time: end time - start time.
        Return none, if the signal is empty (start==None). """

        if self.start: 
            return self.end - self.start
        else:
            return None


    def shift(self,offset,inplace=False):
        """ Add *offset* to signal start and end times and to each signal
        change time. If *inplace* is false, return the result as a new signal
        object. Otherwise, return the result as *self*. """

        # set where to return result
        if inplace:
            sig = self
        else:
            sig = self.clone()

        # add offset
        sig.start += offset
        for i in range(len(self)):
                sig.edges[i] += offset
        sig.end += offset

        return sig


    def reverse(self,inplace=False):
        """ Reverse the signal change times sequence: last change becomes
        the first and viceversa. Time intervals between edges are preserved.
        If *inplace* is false, return the result as a new signal object.
        Otherwise, return the result as *self*. """

        # set where to return result
        if inplace:
            sig = self
        else:
            sig = self.clone()

        # return if nothing to reverse
        if not sig or len(sig) == 0:
            return sig

        # set start level: if times number is odd, must be inverted.
        if len(sig) & 1:
            sig.slevel = not sig.slevel

        # reverse change times, not first and last times (start and end).
        for i in range(len(sig)):
            sig.edges[i] = sig.start + sig.end - sig.edges[i]

        # edges sequence needs to have ascending times
        sig.edges.sort()

        return sig


    def append(self,other):
        """ Return the *self* signal modified by appending *other* signal
        to it. If there is a time gap between the signals, fill it.
        The start time of *other* must be greater or equal to end time of
        *self*. The end level of *self* must be equal to the start level of
        *other*. Otherwise, no append is done. """

        # if other is empty, no append.
        if not other:
            return self

        # if self is empty, copy other into self.
        if not self:
            other.clone_into(self)
            return other

        # check for non overlap
        assert self.end <= other.start, \
                'self and other overlaps in time.\n' \
                + 'self end = ' + str(self.end()) \
                + ' , other start = ' + str(other.start())

        # check for same end-start level
        assert len(self) & 1 ^ self.slevel == other.slevel, \
                'self end level differ from other start level.\n' \
                + 'self end level = ' + str(len(self) & 1 ^ self.slevel) \
                + ' , other start level = ' + str(other.slevel)

        # append edges of other to self
        self.edges += other.edges

        return self


    def split(self,split,inplace=False):
        """ Split the signal into two signals. *split* is the split time.
        Return two signal objects. The first is the part of the original
        signal before the split time, it ends at the split time. The second is
        the part after the split time, it starts at the split time.
        If *split* is equal to a signal change time, the change is put into
        the second part signal.
        If *inplace* is false, the second signal is a new signal object.
        If *inplace* is true, the second signal is put into the *self* signal. 
        If *split* is not inside the original signal domain, no split
        occours, None is returned. """

        # if split outside signal domain, return None.
        if split < self.start or self.end < split:
            return None

        # if split falls on start or end
        if split == self.start:
            if inplace:
                return None, self
            else:
                return None, self.clone()
        elif split == self.end:
            if inplace:
                return self, None
            else:
                return self.clone(), None

        # search split point
        i = 0
        for i in range(len(self)):
            if split <= self.edges[i]:
                break
        else:
            i += 1

        # older signal part: pre split time. 
        older = Signal(self.start,self.edges[0:i],split,slevel=self.slevel,
                tscale=self.tscale)

        # newer signal part: post split time.
        if inplace:
            self.start = split
            self.edges = self.edges[i:]
            self.slevel = len(older) & 1 ^ self.slevel
            newer = self
        else:
            newer = Signal(split,self.edges[i:],self.end,
                slevel=len(older) & 1 ^ self.slevel,tscale=self.tscale)

        return older, newer


    def join(self,other,inplace=False):
        """ Join two signals (*self* and *other*) in one signal. 
        End time of *self* must be less or equal to start time of *other*.
        If there is a time gap between the joining signals, fill it.
        Return a signal object with the join result. If *inplace* is false,
        a new signal object is returned. If *inplace* is true, the join
        result is put into *self* and *self* is returned. Signals with
        different levels at *self* end and at *other* start cannot be joined
        (join returns None). """

        # if self is not before other, return None.
        if self.end > other.start:
            return None

        # if end level of self is equal to start level of other, return None.
        if len(self) & 1 ^ self.slevel != other.slevel:
            return None

        # join
        if inplace:
            self.edges += other.edges
            self.end = other.end
            return self
        else:
            return Signal(self.start,self.edges + other.edges,other.end,
                slevel=self.slevel)


    def chop(self,period,origin=None,max_chops=1000):
        """ Divide the signal into several time contiguous signals with the
        same elapse time equal to *period*. The dividing times sequence
        starts at *origin* and has an element every *period* time, except for
        the last element. It has end time = period * max_chops, if max_chops
        is reached. Otherwise, it has the end time of the chopped signal.
        Return a list with the chopped signals.
        If *origin* is before the signal start, it is moved forward by an
        integer times of period, until it falls into the signal domain.
        If *origin* is none, it is set to self start time by default.
        If *origin* is after the signal end, no chop occours,
        an empty list is returned. """

        # if not defined, set origin default.
        org = origin
        if not origin:
              org = self.start

        # if origin after signal end, return an empty list.
        if self.end <= origin:
            return []

        # preserve original signal from internal manipulations
        signal = self.clone()

        # if origin before signal domain, set it to the first split in
        # signal domain
        if org <= self.start:
            split =  self.start + period - (self.start - org) % float(period)
        # if origin inside signal domain, discard signal part before origin.
        else:
            discard = signal.split(origin,inplace=True)
            split = org + period

        # init loop vars
        chops = []
        # for each chop time, chop signal until max_chops is reached or the
        # signal end is reached.
        for c in range(1,max_chops):
            chop = signal.split(split,inplace=True)
            if chop:
                chops.append(chop[0])
                split += period
            else:
                break

        # if last split beyond signal end, get the residual part. 
        if split > self.end:
            chops.append(signal)

        return chops

 
    def jitter(self,stddev=0):
        """ Add a gaussian jitter to the change times of *self* signal object
        with the given standard deviation *stddev* and zero mean.
        Signal start and end times are unchanged. """

        # if not edges, return
        if not self.edges:
            return

        # first jittered change must fall between start and second change or end
        new_time = self.edges[0] + random.gauss(0.0,stddev)
        if len(self) > 1:
            top_limit = self.edges[1]
        else:
            top_limit = self.end
        if self.start < new_time and  new_time < top_limit:
            self.edges[0] = new_time

        # if only one change, jittering is terminated.
        if len(self) == 1:
            return

        # add jitter to signal all change times except first and last
        for i in range(1,len(self)-1):
            new_time = self.edges[i] + random.gauss(0.0,stddev)
            # if current edge has room to be moved forward or back, add jitter.
            if self.edges[i - 1] < new_time and new_time < self.edges[i + 1]:
                self.edges[i] = new_time

        # last jittered change must fall between the last but one change or end
        new_time = self.edges[-1] + random.gauss(0.0,stddev)
        if self.edges[-2] < new_time and  new_time < self.end:
            self.edges[-1] = new_time


    def __add__(self,other):
        """ Concatenate (join) other to self. """

        return self.join(other)


    def __len__(self):
        """ Return the length of the change times sequence. """

        return len(self.edges)


    def __nonzero__(self):
        """ Return true if the signal is not empty, return false otherwise. """

        return not self.start is None


    def __eq__(self,other):
        """ Equality test between two signals. Return *True* if the
        two signals are equal. Otherwise, return *False*. Can be used
        as the equality operator as in the following example (signal
        a,b are instances of the Signal class)::

            if signal_a == signal_b:
                print 'signal a and b are equal' """

        if not self is None and not other is None:
            return self.__dict__ == other.__dict__
        else:
            return self is other


    def __ne__(self,other):
        """ Inequality test between two signals. Return *True* if the
        two signals are not equal. Otherwise, return *False*. Can be used
        as the inequality operator as in the following example (signal a,b
        are instances of the Signal class)::

            if signal_a != signal_b:
                print 'signal a and b are different'"""

        if not self is None and not other is None:
            return self.__dict__ != other.__dict__
        else:
            return not self is other


    def _intersect(self,other):
        """ Compute the time intersection of two signals, if exists. 
        Return the start and end time of intersection, for each signal,
        return the indexes of the first and last signal changes inside
        the intersection. """

        # check for empty signal
        if not self or not other:
            return None

        # start and end times of signal A and B intersection
        start = max(self.start,other.start)
        end = min(self.end,other.end)

        # if no intersection, return none
        if start >= end:
            return None

        # find index of first edge after start and index of last edge before end.
        # If no edges in start-end range, set indexes to 0.
        
        for ia_start in range(len(self)):
            if self.edges[ia_start] < start:
                continue
            for ia_end in range(-1,-len(self)-1,-1):
                if self.edges[ia_end] <= end:
                    ia_end += len(self) + 1
                    break
            else:
                ia_start = ia_end = 0
            break
        else:
            ia_start = ia_end = len(self)

        for ib_start in range(len(other)):
            if other.edges[ib_start] < start:
                continue
            for ib_end in range(-1,-len(other)-1,-1):
                if other.edges[ib_end] <= end:
                    ib_end += len(other) + 1
                    break
            else:
                ib_start = ib_end = 0
            break
        else:
            ib_start = ib_end = len(other)

        # compute level before first change after start
        slevel_a = self.slevel ^ (ia_start & 1)
        slevel_b = other.slevel ^ (ib_start & 1)

        return start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b


    def _bioper(self,other,operator):
        """ Compute the logic operator of two given signal object: *self* and
        *signal*. Return a signal object with the operator applyed to the two
        input signals. """

        # if one or both operand is none, return none as result.
        if not self or not other:
            return None

        # compute A and B time intersection paramenters.
        # If no intersection, return none.
        intersection = self._intersect(other)
        if not intersection:
            return None
        start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b = \
            intersection

        # optimize result computation when both self and other are constant
        # if self and other are constant, return a constant signal.
        if len(self) < 1 and len(other) < 1:
            return Signal(start,[],end,slevel=operator(self.slevel,other.slevel))
        
        # optimize result computation when self or other is constant
        if len(self) < 1 and not (operator(1,0) ^ self.slevel):
            return Signal(start,[],end,slevel=self.slevel)
        if len(other) < 1 and not (operator(1,0) ^ other.slevel):
            return Signal(start,[],end,slevel=other.slevel)

        # create output signal object
        out_sig = Signal(start,[],end)

        # initial status vars of a two input logic: inputs a and b, output.
        in_a = slevel_a
        in_b = slevel_b
        out_sig.slevel = operator(in_a,in_b)
        out = out_sig.slevel

        # get all edges, one at a time, from the two lists sorted by
        # ascending time, do it until the end of one of the two lists is
        # reached.
        ia = ia_start
        ib = ib_start
        while ia < ia_end and ib < ib_end:
            # get the next edge in time. If the next edge makes a change to the
            # and output, append it to the output anded pulses and update and
            # logic output (a_and_b).
            # Always update logic inputs (a,b) and list pointers (i,j)
            if self.edges[ia] < other.edges[ib]:
                in_a = not in_a
                if out != operator(in_a,in_b):
                    out_sig.edges.append(self.edges[ia])
                    out = not out
                ia = ia + 1
            elif self.edges[ia] > other.edges[ib]:
                in_b = not in_b
                if out != operator(in_a,in_b):
                    out_sig.edges.append(other.edges[ib])
                    out = not out
                ib = ib + 1
            else:
                in_a = not in_a
                in_b = not in_b
                if out != operator(in_a,in_b):
                    out_sig.edges.append(self.edges[ia])
                    out = not out
                ia = ia + 1
                ib = ib + 1

        # if one of A or B is exausted, the requested logic operation
        # is applied to the remaining part of the other and to the
        # terminating level of the first. The output is appended to result.
        if ia == ia_end and ib < ib_end:
            in_a = self.slevel ^ (ia & 1)
            if operator(in_a,0) != operator(in_a,1):
                out_sig.edges.extend(other.edges[ib:ib_end])
        elif ia < ia_end and ib == ib_end:
            in_b == other.slevel ^ (ib & 1)
            if operator(in_b,0) != operator(in_b,1):
                out_sig.edges.extend(self.edges[ia:ia_end])

        return out_sig


    def __and__(self,other):
        """ Compute the logic *and* of two given signal objects: *self* and
        *other*. Return a signal object with the and of the two input
        signals. Can be used as the bitwise and operator as in the following
        example (signal a,b,c are instances of the Signal class)::

            signal_c = signal_a & signal_b
        """

        return self._bioper(other,lambda a,b: a and b)


    def __or__(self,other):
        """ Compute the logic *or* of two given signal objects: *self* and
        *other*. Return a signal object with the or of the two input
        signals. Can be used as the bitwise or operator as in the following
        example (signal a,b,c are instances of the Signal class)::
            
            signal_c = signal_a | signal-b
        """

        return self._bioper(other,lambda a,b: a or b)


    def __xor__(self,other):
        """ Compute the logic *xor* of two given signal objects: *self* and
        *signal*. Return a signal object with the xor of the two input
        signals. Can be used as the bitwise xor operator as in the
        following example (signal a,b,c are instances of the Signal class)::
            
            signal_c = signal_a ^ signal_b
        """

        # if one or both operand is none, return none as result.
        if not self or not other:
            return None

        # compute A and B time intersection paramenters.
        # If no intersection, return none.
        intersection = self._intersect(other)
        if not intersection:
            return None
        start,end,ia_start,ia_end,slevel_a,ib_start,ib_end,slevel_b = \
            intersection

        # create signal object for xor storage
        xor_sig = Signal(start,[],end)

        # set start level
        xor_sig.slevel = slevel_a ^ slevel_b

        # xor is the union of pulse edges sorted by time
        xor_sig.edges = self.edges[ia_start:ia_end]+other.edges[ib_start:ib_end]
        xor_sig.edges.sort()

        # simultaneous edges cancel each other, so, if any, remove them.
        i = 0 
        while i < len(xor_sig) - 1:
            if not xor_sig.edges[i] - xor_sig.edges[i + 1]:
                del xor_sig.edges[i]
                del xor_sig.edges[i]
            else:
                i += 1

        return xor_sig


    def __invert__(self,inplace=False):
        """ Compute the logic *not* of the given signal object: *self*.
        If *inplace* is false, return the result as a new signal object.
        Otherwise, return the result as *self*.
        Can be used as the bitwise not operator as in the following example
        (signal a,b are instances of the Signal class)::
        
            signal_b = ~ signal_a
        """

        # set where to return result
        if inplace:
            sig = self
        else:
            sig = self.clone()

        # apply inversion
        sig.slevel = not sig.slevel

        return sig


    def integral(self,level=1,normalize=False):
        """ Return the integral of a signal object: the elapsed time of all
        periods in which the signal is at the level specified by *level*.
        Output can be absolute (*normalize=False*) or can be normalized
        (*normalize=True*): absolute integral averaged over the whole signal
        domain. The summation is operated on the signal domain only.
         """

        # do summation between first and last signal edges
        edges_int = 0
        for i in range(0,len(self),2):
            try:
                edges_int += self.edges[i + 1] - self.edges[i]
            except:
                edges_int += self.end - self.edges[-1]

        # return summation of level=0 or =1 as requested by level argument
        if level ^ self.slevel:
            integral = edges_int
        else:
            integral = self.end - self.start - edges_int

        # return normalized if requested by normalized argument
        if normalize:
            integral = float(integral) / (self.end - self.start)

        return integral


    def correlation(self,other,mask=None,normalize=False,step_size=1,
            step_left=None,step_right=None):
        """ Return the correlation function of two given signal objects:
        *self* and *other*. If *mask* is defined as signal object, the
        correlation is computed only where mask=1. Output can be absolute:
        integral of xor between shifted *self* and *other* signals
        (*normalize=False*). Output can be normalized (*normalize=True*) in
        the range -1 +1.  The correlation function time scale is set by
        *step_size*.
        The correlation function is returned as two lists: the correlation
        values and the correlation time shifts. The origin of time shift
        is set when the shifted start time of *self* is equal to the start
        time of *other*. *step_left* is the number of steps where to compute
        the correlation function on the left of origin. If it is undefined,
        the number of steps is set automatically to the maximum extent giving
        a non empty intersection among *self* and *other*. The same holds for
        *step_right*. """

        # simplify variables access
        sig_a = self.clone()

        # number of slide steps of A toward left
        left_steps = self.elapse() / step_size
        # since A xor B needs a non null intersection, if step_size is an
        # exact multple of A elapse, go back one step.
        if left_steps > 1. and left_steps % 1. == 0:
            left_steps -= 1

        # if step_left is defined, use it but limit it to left_steps boundary.
        if step_left != None and step_left <= left_steps:
            left_steps = step_left

        # step_lefts need to be integer
        left_steps = int(left_steps)

        # number of slide steps of A toward right
        right_steps = other.elapse() / step_size
        # since A xor B needs a non null intersection, if step_size is an
        # exact multple of B elapse, go back one step.
        if right_steps > 1. and right_steps % 1. == 0:
            right_steps -= 1

        # if step_right is defined, use it but limit it to right_steps boundary.
        if step_right != None and step_right <= right_steps:
            right_steps = step_right

        # step_right need to be integer
        right_steps = int(right_steps)

        # shift that align A start on B start
        shift = other.start - self.start

        # apply shift to slide A to the leftmost position
        sig_a.shift(shift - left_steps * step_size,inplace=True)

        # compute correlation step by step
        corr = []
        shifts = []
        for step in range(-left_steps,right_steps+1):

            # correlation among signal A and B
            if mask:
                xor = (sig_a ^ other) & mask
            else:
                xor = sig_a ^ other
            if normalize:
                corr += [xor.integral(0,normalize) * 2 - 1]
            else:
                corr += [xor.integral(0,normalize=False)]

            shifts += [step * step_size + shift]

            # shift right A by step units
            sig_a.shift(step_size,inplace=True)

        return corr, shifts


    def plot(self,*args,**kargs):
        """ Plot signal *self* as square wave. Requires Matplotlib.
        *\*args* and *\**kargs* are passed on to matplotlib functions."""

        from matplotlib.pyplot import plot, ylim, yticks

        # generate signal levels
        levels = [self.slevel]
        for i in range(len(self)):
            levels += [not levels[-1]]
        levels += [levels[-1]]

        # set proper draw style for square waves
        if not kargs:
            kargs = {}
        kargs.update({'drawstyle':'steps-post'})
        ylim(-0.1,1.1)
        yticks([0,1])

        # if there are given args, pass them
        if args:
            plot([self.start]+self.edges+[self.end],levels,*args,**kargs)
        else:
            plot([self.start]+self.edges+[self.end],levels,**kargs)


    def stream(self,other,elapse,buf_step=1.):
        """ Append *other* signal to *self* signal. If self signal elapse time
        becomes greater than *elapse*, delete from the older part of self until
        its elapse time is less or equal than *elapse*. The elapsed time fo the
        deleted part is forced to a integer multiple of *buf_step*. """

        self.append(other)

        # if self elapse below allowed max, return an empty discarded signal
        # and the "appendend" self.
        if self.elapse() <= elapse:
            return (Signal(),self)

        # compute shift to be applied, if any.
        shift = (int((self.elapse() - elapse) / buf_step) + 1) * buf_step

        # reduce self elapse time below elapse argument
        discard, keep = self.split(self.start + shift)

        # return discarded part (before split) and kept part (after split).
        return (discard,keep)


#### functions

def bin2pwm(bincode,period,elapse_0,elapse_1,active=1,origin=0,tscale=1.):
    """ Convert a binary code into a pulse width modulation signal in
    BTS format. Return a Signal class object. *bincode* is a tuple or a
    list of tuples: (*bit_length*, *bits*). *bit_length* is an integer
    with the number of bits. *bits* is an integer or a long integer with
    the binary code.  First bit is the LSB, last bit is the MSB.
    *period* is the period of pwm pulses. *elapse_0* is the elapse time
    of a pulse coding a 0 bit. *elapse_1*, the same for a 1 bit. *active*
    is the active pulse level. *origin* is the time of the leading edge
    of the first signal pulse. """

    # to list single tuple
    if type(bincode) != list:
        bincode = [bincode]

    # allocate pwm signal
    pwm = Signal(slevel=~active&1,tscale=tscale)

    # set conventional start
    pwm.start = origin

    # convert a tuple at a time
    for bit_num, code in bincode:
        # convert bit by bit of current tuple
        end = bit_num * period + origin
        t0 = origin
        for i in range(bit_num):
            if code & 1:
                t1 = t0 + elapse_1
            else:
                t1 = t0 + elapse_0
            code >>= 1
            pwm.edges.append(t0)
            pwm.edges.append(t1)
            t0 = t0 + period 

        # next tuple start at current tuple end time
        origin = end

    # end signal at the end of last period
    pwm.end = end

    return pwm


def pwm2bin(pwm,elapse_0,elapse_1,active=1,origin=0,period=None,threshold=0.2):
    """ Convert a pulse width modulation signal in BTS format to binary code.
    Return a tuple: see *bincode* in **bin2pwm**. *pwm* is the signal to
    decode. For the other arguments see **bin2pwm**. If *period* is not
    defined, conversion is done by testing only the active pulse level elapse
    against a threshold computed as mean of elapse_0 and elapse_1. No check is
    done on pulse period and decoding consider every pulse. If period is
    set to the modulation pulse period, conversion is done by synchronous
    symbols correlation. The signal is chopped with the given *period*,
    starting from *origin*, start of symbol periods, until signal end. Each
    signal chop, corresponding to one symbol time, is correlated with both
    models of 0 and 1 pulses. The better value above *threshold* is taken as
    result. """

    ## if period, convert by correlation
    if period:

        # if at least not one pulse, return zero code
        if len(pwm) < 2:
            return (0,0), 0

        # build pulse model and mask
        margin = 0.2 * min(elapse_0,elapse_1)
        last = max(elapse_0,elapse_1) + margin
        model_0 = Signal(-margin,[0,elapse_0],last)
        model_1 = Signal(-margin,[0,elapse_1],last)
        mask = Signal(-margin,[-margin,last],last)

        # if active low, force pwm signal to active high
        if not active:
            pwm.slevel = 0

        # if origin not defined, set default value
        split_origin = (max(elapse_0,elapse_1) - period) / 2.
        if not origin:
            split_origin += pwm.edges[0]
        else:
            split_origin += origin

        # chop signal
        chops = pwm.chop(period,split_origin)

        # for each symbol period
        code = 0
        error = 0
        for chop in chops[-2::-1]:
            code <<= 1
            error <<= 1
            chop.shift(-chop.edges[0],inplace=True)
            corr_0 = (chop ^ model_0 & mask).integral(level=0,normalize=True)
            corr_1 = (chop ^ model_1 & mask).integral(level=0,normalize=True)
            if abs(corr_0 - corr_1) > threshold:
                if corr_0 < corr_1:
                    code |= 1
            else:
                error |= 1

        # if active level is low, restore it into pwm signal
        if not active:
            pwm.slevel = 1
        return (len(chops)-1,code), error

    ## if not period, convert by pulse elapse time
    else:
        code = 0
        threshold = (elapse_0 + elapse_1) / 2.
        one_is_above = elapse_0 < elapse_1
        start_off = (len(pwm) & 1) + 2

        for i in range(len(pwm)-start_off,-1,-2):
            code <<= 1
            if pwm.edges[i + 1] - pwm.edges[i] > threshold:
                if one_is_above:
                    code |= 1
            else:
                if not one_is_above:
                    code |= 1

        return len(pwm) / 2, code


def serial_tx(chars,times,char_bits=8,parity='off',stop_bits=2,baud=50,
        tscale=1.):
    """ Simulate a serial asynchronous transmitting interface. Return
    a BTS signal with the serial line pulses coding a given list of
    characters, according to the following serial parameters. The list of
    *chars* is the input to the serial transmitter. *times* is the list
    of the start bit rising edge time of each char in *chars*. If times
    are too fast with respect to the current baud rate, a char fifo behavoiur
    is activated. *char_bits* is the character size in bits (5,6,7,8).
    *parity* is the parity bit even, odd or off (parity absent).
    *stop_bits* is the number of stop bits (1,2). *baud* is the serial
    line speed, any positive value is allowed. The serial line is assumed
    active high. """

    # init serial line signal 
    sline = Signal(times[0]-0.1/baud,[],None,slevel=0,tscale=tscale)

    # bit period
    bit_time = tscale / baud

    # serial char start time
    prev_start = 0

    # serialize all chars
    for char, start in zip(chars,times):

        # if char is too fast, delay it as a fifo.
        if prev_start > start:
            start = prev_start

        # make serial code start at given timing
        sline.edges.append(start)
            
        # serialize char bits: LSB first.
        line = 1
        schar = ord(char)
        for c in range(1,char_bits + 1):
            if not line ^ schar & 1:
                sline.edges.append(start + c * bit_time)
                line = not line
            schar >>= 1
            
        # if required add parity
        if parity != 'off':

            # strip character don't care bits
            mask = 0x1f
            for i in range(char_bits-5):
                mask <<= 1
                mask |= 1
            char = ord(char) & mask

            # compute parit bit
            ones = __parity(char)

            # set it into serial signal
            if parity == 'odd':
                ones = ones ^ 1
            c = c + 1
            if not line ^ ones:
                sline.edges.append(start + c * bit_time)
                line = not line

        # stop bits: if not yet 0, set pulse level to 0.
        c = c + 1
        if line:
            sline.edges.append(start + c * bit_time)

        # next start
        start = start + (c + stop_bits) * bit_time

    # set signal end with last char end    
    sline.end = start


    return sline


# serial rx character status bits
PARITY_ERROR = 0x01
STOP_ERROR = 0x02
# serial rx, End Of Signal error codes:
# EOS while start bit, char bits, parity bit, stop bits.
EOS_START = 0x10
EOS_CHAR = 0x20
EOS_PARITY = 0x30
EOS_STOP = 0x40


def serial_rx(sline,char_bits=8,parity='off',stop_bits=2,baud=50):
    """ Simulate a serial asynchronous receiving interface. Return
    a list of the received characters, a list of their start times and
    a list of their status: 0 = ok, 1 = parity error. *sline*
    is a BTS signal with the serial line pulses coding the characters to be
    received. For the keyword arguments see **serial_tx**. The serial line
    pulses are sampled at the given baud rate like a real asynchronous
    serial interface. """

    # constant
    char_mask = [0,0,0,0,0,0x10,0x20,0x40,0x80]

    # returned lists
    chars = []
    timings = []
    status = []

    # init vars
    bit_time = float(sline.tscale) / baud
    tpos = 0 
    imax = len(sline)
    start = sline.start
    char = 0
    # consume all serial line pulses
    while True:

        # search the first signal edge after start, stop at the last edge.
        level, tpos = sline.level(start,tpos)

        # if start goes beyond the last edge, terminate.
        if level is None:
            return chars, timings, status

        # if start falls into zero level, move start to next rising edge.
        if level:
            tpos += 1
            try:
                start = sline.edges[tpos]
            # if no more edges, terminate.
            except:
                return chars, timings, status

        # center sampling time to the middle of bit period
        sample_time = start + bit_time / 2.

        # sample start bit, search first signal edge after sampling,
        # stop at the last edge.
        level, tpos = sline.level(sample_time,tpos)
        # if start bit sampling  goes beyond the last edge, terminate.
        if level is None:   
            status.append(EOS_START)
            chars.append(chr(0))
            timings.append(start)
            return chars, timings, status

        # detect line level at sampling time. If it is 0,
        # character start is aborted, go to the begining.
        if level:
            start = sample_time
            continue

        # presume OK for rx char status
        status.append(0)

        # sample a char, char bits wide: LSB first.
        for c in range(char_bits,0,-1):
            sample_time += bit_time
            level, tpos = sline.level(sample_time,tpos)
            # if character sampling goes beyond the signal end, set
            # remaining char bit to zero and terminate.
            if level is None:
                for j in range(c):
                    char >>= 1
                    char |= char_mask[char_bits]
                chars.append(chr(char))
                timings.append(start)
                status[-1] |= EOS_CHAR
                return chars, timings, status
            char >>= 1
            if level:
                char |= char_mask[char_bits]
        chars.append(chr(char))
        timings.append(start)

        # if required, check parity
        if parity != 'off':

            # compute parit bit
            ones = __parity(char)
            if parity == 'odd':
                ones = ones ^ 1

            # sample parity bit, stop at the signal end.
            sample_time += bit_time
            level, tpos = sline.level(sample_time,tpos)
            # if parity bit sampling goes beyond the signal end, terminate.
            if level is None:
                status[-1] |= EOS_PARITY
                return chars, timings, status
            else:
                parity_bit = level

            # check
            if parity_bit != ones:
                status[-1] |= PARITY_ERROR

        # sample stop bit(s)
        for s in range(stop_bits):
            sample_time += bit_time
            level, tpos = sline.level(sample_time,tpos)
            # if character sampling goes beyond the signal end, set
            # remaining char bit to zero and terminate.
            if level is None:
                status[-1] |= EOS_STOP
                return chars, timings, status
            # if level at stop sampling is 0, set error and go to next char
            elif level == 0:
                status[-1] |= STOP_ERROR

        # move start of next char at stop bits end.
        start = sample_time + 0.5 * bit_time

    return chars, timings, status


def __parity(value):
    """ Return 0 for even parity, 1 for odd parity in value"""
    ones = 0
    while value:
        value &= value - 1
        ones += 1
    return ones & 1


def noise(origin,end,period_mean=1,period_stddev=1,
        width_mean=1,width_stddev=1,active='random'):
    """ Return a signal object with random pulses. *origin* is
    the time of the first pulse trailing edge. *end* is the signal
    end time. Pulses
    period and width follow a gaussian distribution: *period_mean* and
    *period_stddev* are the given mean and standard deviation of pulses
    period, *width_mean* and *width_stddev* are the given mean and
    standard deviation of the pulse width at 1 level. *active* is the
    active pulse level, can be 0,1,'random'. """

    # allocate noise signal
    noise = Signal()

    # if required, set a random start level. Else default to level 0.
    if active == 'random':
        noise.slevel = random.randint(0,1)
    elif active == 0:
        noise.slevel = 1
    else:
        noise.slevel = 0

    # set start just before origin and end
    noise.start = origin - period_mean / 100.
    noise.end = end

    # level 0 mean and stdev from frequency and pulse width moments
    pause_mean = period_mean - width_mean
    pause_stddev = math.sqrt(period_stddev**2 + width_stddev**2) / 2

    # insert first pause interval end
    last_pause_end = \
            abs(random.gauss(pause_mean,pause_stddev)) + origin
    if last_pause_end > end:
        return

    # make noise pulses
    while True:
        # not really true gauss: negative branch reflected over positive.
        width = abs(random.gauss(width_mean,width_stddev))
        pause = abs(random.gauss(pause_mean,pause_stddev))
        if last_pause_end + width + pause > end:
            break
        noise.edges.append(last_pause_end)
        noise.edges.append(last_pause_end + width)
        last_pause_end = last_pause_end + width + pause

    return noise


def square(origin,end,period,width,active=1):
    """ Return a signal object with a square wave with constant period
    and constant duty cycle. *origin* is the time of the first pulse
    trailing edge. *end* is the signal end time. *period* is the pulse
    period. *width* is the pulse width at active level. """

    # allocate signal
    square = Signal()

    # set start level according to active level
    square.slevel = ~ active & 1

    # set start just before origin
    square.start= origin - period / 100.

    # insert first pause interval end
    while origin < end:
        square.edges.append(origin)
        square.edges.append(origin + width)
        origin = origin + period

    # set end
    square.end = end

    return square

#### END
