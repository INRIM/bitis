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
        """ Prepare testing signals """

        # test signal instance
        self.test = vb.Signal()
        self.test.test()

        # test signals: a base signal and its shifted copies.
        # Graph of base signal __|^|_|^^ """
        times = [0,2,3,4,6]
        self.base = vb.Signal(times,slevel=0,tscale=1)
        self.shift1 = vb.Signal([i + 1 for i in times],slevel=0,tscale=1)
        self.shift2 = vb.Signal([i + 2 for i in times],slevel=0,tscale=1)
        self.shift3 = vb.Signal([i + 3 for i in times],slevel=0,tscale=1)
        self.shift4 = vb.Signal([i + 4 for i in times],slevel=0,tscale=1)
        self.shift5 = vb.Signal([i + 5 for i in times],slevel=0,tscale=1)
        self.shift6 = vb.Signal([i + 6 for i in times],slevel=0,tscale=1)
        self.shift7 = vb.Signal([i + 7 for i in times],slevel=0,tscale=1)


    def test_clone(self):
        """ Test creation of an identical copy of signal. """

        # compare original test signal and output signal
        self.assertEqual(self.test,self.test.clone())


    def test_shift(self):
        """ Test signal shifting. """

        # shift forward, backward and to same place again
        testing= self.test.clone()
        testing.shift(13)
        testing.shift(-23)
        testing.shift(10)

        # test expected offsets
        self.assertEqual(self.test,testing)


    def test_reverse(self):
        """ Test signal edge reversing. """

        # reverse 
        testing = self.base.clone()
        testing.reverse()

        # compare expected signal and testing result
        expected = vb.Signal([0,2,3,4,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)


    def test__intersect(self):
        """ Test intersection parameters. """

        testing = self.base._intersect(self.base)
        self.assertEqual((0,6,1,3,0,1,3,0),testing)

        testing = self.base._intersect(self.shift1)
        self.assertEqual((1,6,1,3,0,1,3,0),testing)

        testing = self.base._intersect(self.shift2)
        self.assertEqual((2,6,2,3,1,1,2,0),testing)

        testing = self.base._intersect(self.shift3)
        self.assertEqual((3,6,3,3,0,1,1,0),testing)

        testing = self.base._intersect(self.shift4)
        self.assertEqual((4,6,4,3,1,1,0,0),testing)

        testing = self.base._intersect(self.shift5)
        self.assertEqual((5,6,4,3,1,1,0,0),testing)
        # sospetto ? B non correttamente detettato

        testing = self.base._intersect(self.shift6)
        self.assertEqual(None,testing)

        testing = self.base._intersect(self.shift7)
        self.assertEqual(None,testing)


    def test_invert(self):
        """ Test logical not on test signal. """

        # from original signal to itself through a doble not
        testing = ~ ~self.base

        # compare original test signal and output signal
        self.assertEqual(self.base,testing)


    def test_and(self):
        """ Test logical and on test signal. """

        testing = self.base & self.base
        self.assertEqual(self.base,testing)

        testing = self.base & self.shift1
        expected = vb.Signal([1,5,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base & self.shift2
        expected = vb.Signal([2,4,5,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base & self.shift3
        expected = vb.Signal([3,5,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base & self.shift4
        expected = vb.Signal([4,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base & self.shift5
        expected = vb.Signal([5,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base & self.shift6
        expected = None
        self.assertEqual(expected,testing)

        testing = self.base & self.shift7
        expected = None
        self.assertEqual(expected,testing)


    def test_or(self):
        """ Test logical or on test signal. """

        testing = self.base | self.base
        self.assertEqual(self.base,testing)

        testing = self.base | self.shift1
        expected = vb.Signal([1,2,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base | self.shift2
        expected = vb.Signal([2,3,4,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base | self.shift3
        expected = vb.Signal([3,4,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base | self.shift4
        expected = vb.Signal([4,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base | self.shift5
        expected = vb.Signal([5,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)


    def test_xor(self):
        """ Test logical xor on test signal. """

        testing = self.base ^ self.base
        expected = vb.Signal([0,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift1
        expected = vb.Signal([1,2,5,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift2
        expected = vb.Signal([2,3,5,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift3
        expected = vb.Signal([3,4,5,6],slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift4
        expected = vb.Signal([4,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift5
        expected = vb.Signal([5,6],slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift6
        expected = None
        self.assertEqual(expected,testing)

        testing = self.base ^ self.shift7
        expected = None
        self.assertEqual(expected,testing)


    def test_logic(self):
        """ Test signal logic functions by computing the xor of two
        signals in two ways. The first, directly by xor method. The
        second using the equation a xor b = a and not b or not a and b. """

        # make repeatable random sequences
        random.seed(1)

        # iterate test on several random signals
        for t in range(20):

            # create random signals
            in_a = vb.Signal()
            in_a.noise(0,100,freq_mean=0.1,width_mean=3)
            in_b = vb.Signal()
            in_b.noise(-10,90,freq_mean=0.3,width_mean=2)

            # direct xor
            xor1 = in_a ^ in_b

            # xor from equation
            xor2 = in_a & ~in_b | ~in_a & in_b

            # compare original test signal and output signal
            self.assertEqual(xor1,xor2)


    def test_integral(self):
        """ Test integral of signal computation. """

        self.assertEqual(30,self.test.integral(1))
        self.assertEqual(33,self.test.integral(0))
        self.assertEqual(33,(~self.test).integral(1))
        self.assertEqual(30,(~self.test).integral(0))


    def test_correlation(self):
        """ Test correlation function of two signals (*self* and *other*). """

        # make repeatable random sequences
        random.seed(1)

        # iterate test on several random signals
        for t in range(1):

            # create random signals
            in_a = vb.Signal()
            in_a.noise(0,7)
            in_b = vb.Signal()
            in_b.noise(0,7)

            # compute dumb correlation
            expected = dumb_correlation(in_a,in_b,normalize=False)
            testing = in_a.correlation(in_b,normalize=False)
            print 'expected=',expected
            print 'testing=',testing

#            self.assertEqual(expected,testing)

            # compare original test signal and output signal
            pl.figure(1)
            pl.subplot(4,1,1)
            pl.xlim(0,10)
            pl.ylim(-0.1,1.1)
            in_a.plot() 
            pl.subplot(4,1,2)
            pl.xlim(0,10)
            pl.ylim(-0.1,1.1)
            in_b.plot() 
            pl.subplot(4,1,3)
            pl.grid()
            corr, times = expected
            pl.plot(times,corr)
            pl.subplot(4,1,4)
            pl.grid()
            corr, times = testing
            pl.plot(times,corr)
            pl.show()


def dumb_correlation(self,other,normalize=False):
        """ Returns the unormalized correlation function of two signals
        (*self* and *other*). """

        # simplify variables access
        sig_a = self.clone()

        # take the first edge of signal B as origin. Keep signal B fixed in
        # time and slide signal A. To start, shift A to put A end on B start.
        shift = other.times[0] - self.times[-1]
        for i in range(len(sig_a.times)):
            sig_a.times[i] = sig_a.times[i] + shift

        # compute correlation
        corr = []
        times = []
        for t in range(self.times[-1] - self.times[0]
                + other.times[-1] - other.times[0] - 1):

            # shift right A by 1 unit
            for i in range(len(sig_a.times)):
                sig_a.times[i] = sig_a.times[i] + 1

            # correlation among signal A and B
            if normalize:
                corr += [(sig_a ^ other).integral(0,normalize) * 2 - 1]
            else:
                corr += [(sig_a ^ other).integral(0,normalize=False)]

            times += [t + shift + 1]

        return corr, times


# main
if __name__ == '__main__':
    unittest.main()

#### END
