#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import sys
sys.path.append('..')

import numpy as np

from src.language import LanguagePython
from src.parser_text import ParserText
from src.formatter import Formatter

from test_parsing_python import ParserPythonCheck

class ParserOptimizeCheck(ParserPythonCheck):

    def setUp(self):
        self.parser = ParserText(LanguagePython(int2float=False))
        self.formatter = Formatter(LanguagePython(int2float=False))
    
    
    def calc(self, s, glob=None):
        self.parser.parse_text(s)
        self.parser.optimize_runtime()
        
        # add a line for setting the result in order to be able to compare it
        tokens = self.parser.result
        tokens[-1] = { 'op':'=', 'pos':'infix', 'args':['result', tokens[-1]] }
        expr = self.formatter(tokens)
        if glob is not None:
            for k, v in glob.iteritems():
                expr = expr.replace(k, str(v))
                
        # execute python code
        exec(expr)
        
        # return result
        return locals()['result']


    def parse(self, s):
        self.parser.parse_text(s)
        self.parser.optimize_runtime()
        return self.formatter(self.parser)


    def test_optimize(self):
        self.assertEqual(self.parse("4"), "4")
        self.assertEqual(self.parse("a = 9"), "a = 9")
        self.assertEqual(self.parse("-(4+5)"), "-(4 + 5)")
        self.assertEqual(self.parse("a=sin(x)\nb=sin(x)"),
                         "t_0 = np.sin(x)\na = t_0\nb = t_0")
        self.assertEqual(self.parse("sin(a)**(b**c)\nsin(a)**(b**c)+sin(a)"),
                    "t_1 = np.sin(a)\nt_0 = t_1 ** (b ** c)\nt_0\nt_0 + t_1")
        

if __name__ == "__main__":
    unittest.main()
