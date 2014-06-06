#!/usr/bin/env python

import unittest2 as unittest

import sys
import random
sys.path.append('..')

import numpy as np

from src.parser_line import ParserLine
from src.language import LanguagePython
from src.formatter import Formatter

class ParserPythonCheck(unittest.TestCase):
    
    ops = ('*', '/', '+', '-')
    op_prob = 0.5
    
    def setUp(self):
        self.parser = ParserLine(LanguagePython(int2float=False))
        self.formatter = Formatter(LanguagePython())

    
    def calc(self, s, glob=None):
        results = self.parser.parse_string(s)
        return eval(self.formatter(results), glob)

    
    def show_parse(self, s):
        print self.parser.parse_string(s)
        print self.parser.expr_stack
        print self.parser.get_nested_structure()
        print self.formatter(self.parser)


    def _get_token(self, depth=0):
        if random.random() < self.op_prob and depth < 10:
            op = random.choice(self.ops)
            arg1 = self._get_token(depth+1)
            arg2 = self._get_token(depth+1)
            return "(%s %s %s)" % (arg1, op, arg2)
        else:
            return str(random.uniform(-2, 2))


    def test_parse_rnd(self):
        for _ in range(20):
            expr = self._get_token()
            self.assertAlmostEqual(self.calc(expr), eval(expr))


    def test_parse(self):
        self.assertEqual(self.calc("9"), 9)
        self.assertEqual(self.calc("-9"), -9)
        self.assertEqual(self.calc("--9"), 9)
        self.assertEqual(self.calc("9 + 3 + 6"), 9 + 3 + 6)
        self.assertEqual(self.calc("-6 + 3"), -3)
        self.assertEqual(self.calc("9 + 3. / 11"), 9 + 3.0 / 11)
        self.assertEqual(self.calc("(9 + 3)"), (9 + 3))
        self.assertEqual(self.calc("(9+3.) / 11"), (9+3.0) / 11)
        self.assertEqual(self.calc("9 - 12 - 6"), 9 - 12 - 6)
        self.assertEqual(self.calc("9 - (12 - 6)"), 9 - (12 - 6))
        self.assertEqual(self.calc("2*3.14159"), 2*3.14159)
        self.assertEqual(self.calc("3.1415926535*3.1415926535 / 10"), 3.1415926535*3.1415926535 / 10)
        self.assertEqual(self.calc("np.pi * np.pi / 10"), np.pi * np.pi / 10)
        self.assertEqual(self.calc("np.pi*np.pi/10"), np.pi*np.pi/10)
        self.assertEqual(self.calc("np.pi**2"), np.pi**2)
        self.assertEqual(self.calc("round(np.pi**2)"), round(np.pi**2))
        self.assertEqual(self.calc("6.02e23 * 8.048"), 6.02e23 * 8.048)
        self.assertEqual(self.calc("np.e / 3"), np.e / 3)
        self.assertEqual(self.calc("sin(np.pi/2)"), np.sin(np.pi/2))
        self.assertEqual(self.calc("trunc(np.e)"), int(np.e))
        self.assertEqual(self.calc("trunc(-np.e)"), int(-np.e))
        self.assertEqual(self.calc("round(np.e)"), round(np.e))
        self.assertEqual(self.calc("round(-np.e)"), round(-np.e))
        self.assertAlmostEqual(self.calc("np.e**np.pi"), np.exp(np.pi))
        self.assertEqual(self.calc("2**3**2"), 2**3**2)
        self.assertEqual(self.calc("2**3+2"), 2**3+2)
        self.assertEqual(self.calc("2**9"), 2**9)
        self.assertEqual(self.calc("sign(-2)"), -1)
        self.assertEqual(self.calc("sign(0)"), 0)
        self.assertEqual(self.calc("sign(0.1)"), 1)
        self.assertEqual(self.calc("sin(np.pi - np.pi)"), 0.)
        self.assertEqual(self.calc("sin(np.pi/(sign(0.1)+sign(5)))"), np.sin(np.pi/2.))
        self.assertEqual(self.calc("sin(0.)"), 0.)
        self.assertEqual(self.calc("np.e**1."), np.e)
        self.assertEqual(self.calc("np.e**(3-2)"), np.e)
        self.assertEqual(self.calc("(1+2)**2"), 9)        


    def test_parse_eqation(self):
        self.assertEqual(self.calc("3 == 5"), False)
        self.assertEqual(self.calc("3 == 4-1"), True)
        self.assertEqual(self.calc("(a+b)**2 == 9", {"a":1, "b":2}), True)
        self.assertEqual(self.calc(
            "sin(1.)**(2.**3.) - sin(1.)**(2.**3.) + sin(1.) == sin(1.)"), True)


if __name__ == "__main__":
    unittest.main()
