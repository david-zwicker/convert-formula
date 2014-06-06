#!/usr/bin/env python

import sys
sys.path.append( '../..' )

import numpy as np

from ConvertFormula.parser_line import ParserLine
from ConvertFormula.language import LanguagePython, LanguageMathematica
from ConvertFormula.parser_text import ParserText
from ConvertFormula.formatter import Formatter

parser_python = ParserLine( LanguagePython() )
parser_mathematica = ParserLine( LanguageMathematica() )
parser_text = ParserText( LanguageMathematica() )
formatter = Formatter( LanguagePython() )


def parse_line( s, style='python' ):
    if style == 'python':
        parser = parser_python
    else:
        parser = parser_mathematica
    parser.parse_string( s )
    print 'parse:', parser.result_parse
    print 'stack:', parser.result_stack
    print 'nested:', parser.result_nested
    print formatter( parser )
    print s


def parse_text( s, optimize=True ):
    parser_text.parse_text( s )
    parser_text.get_cost()
    print parser_text.result
    print formatter( parser_text )
    #print parser.expr_stack
    if optimize:
        print parser_text.get_cost()
        print parser_text.optimize_runtime()
        print formatter( parser_text )


#print parser.parse_string( "var = unknown(0.) + unknown" )
#print parser.expr_stack
#print parser.get_nested_structure()
#print ParserOutputPython()( parser )

#show_parse( "4", False )
#show_parse( "-(4+5)", False )

#parse_line( "f(3+5*exp(6), g(4+sin(4)))" )
parse_line( "9 + 3 + 4" )
#parse_text( "fA[phiA0, phiB0] - fA[phiA1, phiB1]", True )

# test right order of optimization
#parse_text( "sin[a]^(b^c)\nsin[a]^(b^c)+sin[a]", True )
#parse_line( "((lambdam*R)*(Ecp^2))" )
#parse_line("C1 = (DB*Eim)",'m')
parse_line( "a = 4")
parse_line( "C[1,2] = r + 4" )
