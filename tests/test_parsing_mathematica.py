#!/usr/bin/env python

import unittest2 as unittest

import sys
import random
sys.path.append('..')

import numpy as np

from src.parser_line import ParserLine
from src.language import LanguageMathematica, LanguagePython
from src.formatter import Formatter

class ParserMathematicaCheck(unittest.TestCase):

    ops = ('*', '/', '+', '-')
    op_prob = 0.5

    def setUp(self):
        self.parser = ParserLine(LanguageMathematica())
        self.formatter = Formatter(LanguagePython())


    def calc(self, s):
        results = self.parser.parse_string(s)
        return eval(self.formatter(results), None, {'pi':np.pi, 'e':np.e})


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
        for i in range(20):
            expr = self._get_token()
            self.assertAlmostEqual(self.calc(expr), eval(expr) )


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
        self.assertEqual(self.calc("Pi * Pi / 10"), np.pi * np.pi / 10)
        self.assertEqual(self.calc("Pi*Pi/10"), np.pi*np.pi/10)
        self.assertEqual(self.calc("Pi^2"), np.pi**2)
        self.assertEqual(self.calc("Round[Pi^2]"), round(np.pi**2))
        self.assertEqual(self.calc("6.02E23 * 8.048"), 6.02E23 * 8.048)
        self.assertEqual(self.calc("e / 3"), np.e / 3)
        self.assertEqual(self.calc("Sin[Pi/2]"), np.sin(np.pi/2))
        self.assertEqual(self.calc("Trunc[E]"), int(np.e))
        self.assertEqual(self.calc("Trunc[-E]"), int(-np.e))
        self.assertEqual(self.calc("Round[E]"), round(np.e))
        self.assertEqual(self.calc("Round[-E]"), round(-np.e))
        self.assertAlmostEqual(self.calc("E^Pi"), np.exp(np.pi))
        self.assertEqual(self.calc("2^3^2"), 2**3**2)
        self.assertEqual(self.calc("2^3+2"), 2**3+2)
        self.assertEqual(self.calc("2^9"), 2**9)
        self.assertEqual(self.calc("Sign[-2]"), -1)
        self.assertEqual(self.calc("Sign[0]"), 0)
        self.assertEqual(self.calc("Sign[0.1]"), 1)
        self.assertEqual(self.calc("Sin[Pi - Pi]"), 0.)
        self.assertEqual(self.calc("Sin[Pi/(Sign[0.1]+Sign[5])]"), np.sin(np.pi/2.))
        self.assertEqual(self.calc("Sin[0.]"), 0.)
        self.assertEqual(self.calc("E^1."), np.e)
        self.assertEqual(self.calc("E^(3-2)"), np.e)
        self.assertEqual(self.calc("(1+2)^2"), 9)


if __name__ == "__main__":
    unittest.main()
