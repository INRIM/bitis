#!/usr/bin/python
# .+
# .context    : Vectorial Binary Signal Processing Library
# .title      : Test Suite
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
# .-

import vebis as vb
import random
import unittest

import matplotlib.pyplot as pl


class TestVebis(unittest.TestCase):

    def setUp(self):

        # test signal instance
        self.signal = vb.Signal()
        self.signal.test()


    def test_clone(self):
        """ Test creation of an identical copy of signal. """

        # compare original test signal and output signal
        self.assertEqual(self.signal,self.signal.clone())


    def test_shift(self):
        """ Test signal shifting. """

        # shift forward, backward and to same place again
        original = self.signal.clone()
        self.signal.shift(13)
        self.signal.shift(-23)
        self.signal.shift(10)

        # test expected offsets
        self.assertEqual(original,self.signal)


    def test_reverse(self):
        """ Test signal edge reversing. """

        # reverse twice
        original = self.signal.clone()
        self.signal.reverse()
        self.signal.reverse()

        # compare original test signal and output signal
        self.assertEqual(original,self.signal)


    def test__intersect(self):
        """ Test creation of an identical copy of signal. """

        # compare original test signal and output signal
        result = vb.Signal((0,6,[1,2,3,4]))._intersect(
                vb.Signal((-1,8,[2,3,4,5,7,8])))
        self.assertEqual((0,6,0,3,0,0,3,0),result)


    def test_invert(self):
        """ Test logical not on test signal. """

        # make repeatable random sequences
        random.seed(1)

        # iterate test on several random signals
        for t in range(20):

            # create random signal
            signal_in = vb.Signal()
            signal_in.noise(0,50)

            # from original signal to itself through a doble not
            signal_out = ~ ~signal_in

            # compare original test signal and output signal
            self.assertEqual(signal_in,signal_out)


    def test_logic(self):
        """ Test signal logic functions by computing the xor of two
        signals in two ways. The first, directly by xor method. The
        second using the equation a xor b = a and not b or not a and b. """

        # make repeatable random sequences
        random.seed(1)

        # iterate test on several random signals
        for t in range(1):

            # create random signals
            in_a = vb.Signal()
            in_a.noise(0,20)
            in_b = vb.Signal()
            in_b.noise(0,20)

            # direct xor
            xor1 = in_a ^ in_b

            # xor from equation
            xor2 = in_a & ~in_b | ~in_a & in_b

            # compare original test signal and output signal
            self.assertEqual(xor1,xor2)


    def test_integral(self):
        """ Test integral of signal computation. """

        self.assertEqual(30,self.signal.integral(1))
        self.assertEqual(33,self.signal.integral(0))
        self.assertEqual(33,(~self.signal).integral(1))
        self.assertEqual(30,(~self.signal).integral(0))


    def test_correlation(self):
        """ Test correlation function of two signals (*self* and *other*). """

        # make repeatable random sequences
        random.seed(1)

        # iterate test on several random signals
        for t in range(1):

            # create random signals
            in_a = vb.Signal()
            in_a.noise(0,6)
            in_b = vb.Signal()
            in_b.noise(0,6)

            # compute dumb correlation
            corr, times = dumb_correlation(in_a,in_b)

            # compare original test signal and output signal
            #self.assertEqual(xor1,xor2)
            pl.figure(1)
            pl.subplot(3,1,1)
            pl.xlim(0,10)
            pl.ylim(-0.1,1.1)
            in_a.plot() 
            pl.subplot(3,1,2)
            pl.xlim(0,10)
            pl.ylim(-0.1,1.1)
            in_b.plot() 
            pl.subplot(3,1,3)
            pl.grid()
            pl.plot(times,corr)
            pl.show()


def dumb_correlation(self,other):
        """ Returns the unormalized correlation function of two signals
        (*self* and *other*). """

        # simplify variables access
        sig_a = self.clone()
        print 'other=',other
        print 'sig_a=',sig_a

        # take the first edge of signal B as origin. Keep signal B fixed in
        # time and slide signal A. To start, shift A to put A end on B start.
        shift = other.stime - sig_a.etime
        sig_a.stime = sig_a.stime + shift
        sig_a.etime = sig_a.etime + shift
        for i in range(len(sig_a.ctimes)):
            sig_a.ctimes[i] = sig_a.ctimes[i] + shift

        # compute correlation
        corr = []
        times = []
        for t in range(self.etime-self.stime+other.etime-other.stime-1):

            # shift right A by 1 unit
            sig_a.stime = sig_a.stime + 1
            sig_a.etime = sig_a.etime + 1
            for i in range(len(sig_a.ctimes)):
                sig_a.ctimes[i] = sig_a.ctimes[i] + 1

            print 'sig_a=',sig_a
            print 'XOR=',sig_a ^ other
            # correlation among signal A and B
            corr += [(sig_a ^ other).integral(0,mean=True) * 2 - 1]
            times += [t + shift + 1]
            print 'corr=',corr
            print 'times=',times

        return corr, times


# main
if __name__ == '__main__':
    unittest.main()

#### END
