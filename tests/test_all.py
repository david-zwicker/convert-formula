#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from test_optimizing import *
from test_parsing_python import *
from test_parsing_mathematica import *

if __name__ == "__main__":
    unittest.main()
