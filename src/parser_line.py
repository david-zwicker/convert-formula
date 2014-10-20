""" Defines classes for parsing mathematical formulas according to various
language definitions.

This parser was build based on the code `fourFn.py` given in the example section
of the pyparsing webpage. The code was written by `Paul McGuire`.
"""

import copy
from pyparsing import Optional, ZeroOrMore, Forward, downcaseTokens
from .language import LanguageBase


def _show_token(strg, loc, toks):
    """ Auxilariy function for printing the current token """
    print("Strg: %r" % strg)
    print("Loc: %r" % loc)
    print("Toks: %r" % toks)


class ParserLine(object):
    """ Base class describing a generic parser handling input in a 'common'
    style """
    
    def __init__(self, language):
        """ Initializes the parser """
        
        if isinstance(language, LanguageBase):
            self.language = language
        else:
            raise ValueError('`language` is not of type LanguageBase')

        self.result_parse = []
        self.result_stack = []
        self.result_nested = None
        self.parser = self.init_parser()


    def set_assignment(self, strg, loc, toks):
        """ Helper function used to remember the variable the value is assigned
        to """
        if len(toks) > 0:
            self.assignment = toks[0]


    def push_first(self, strg, loc, toks):
        """ Helper function for creating the expression stack """
        if len(toks) > 0:
            self.result_stack.append(toks[0])
            #if toks and len(toks)>1 and toks[0].isalpha():
            #    self.result_stack.append('FCALL')


    def push_unary_minus(self, strg, loc, toks):
        """ Helper function for pushing the unary minus onto the expression
        stack """
        if toks and toks[0] == '-':
            self.result_stack.append('UNARY-')
            #~ self.exprStack.append('-1')
            #~ self.exprStack.append('*')


    def _push2stack(self, value):
        """ returns a function which pushes `value` to the expression stack.
        This function migth be used as a ParseAction """
        return lambda s, l, t: self.result_stack.append(value)


    def init_parser(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: real | Word(alphas) | array | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        
        atoms = self.language.get_parser_atoms()

        variable = atoms['variable']#.setParseAction(downcaseTokens)

        func_lpar  = atoms['func_lpar'].setParseAction(self._push2stack('('))
        func_delim = atoms['func_delim']
        func_rpar  = atoms['func_rpar'].setParseAction(self._push2stack(')'))

        array_lpar  = atoms['array_lpar'].setParseAction(self._push2stack('['))
        array_delim = atoms['array_delim']
        array_rpar  = atoms['array_rpar'].setParseAction(self._push2stack(']'))

        lpar   = atoms['lpar'].suppress()
        rpar   = atoms['rpar'].suppress()
        expop  = atoms['exp']
        
        addop  = atoms['plus'] | atoms['minus']
        multop = atoms['mult'] | atoms['div']
        cmpop  = atoms['equal']

        expr = Forward() # forward declaration of an entire expression
        # this is necessary for defining the recursive grammar
        
        # smallest entity of a mathematical expression:
        array = variable + \
            array_lpar + \
            atoms['int'].addParseAction(self.push_first) + \
            ZeroOrMore(array_delim + atoms['int']) + \
            array_rpar
        
        func_call = atoms['function'].setParseAction(downcaseTokens) + \
            func_lpar + \
            expr + \
            ZeroOrMore(func_delim + expr) + \
            func_rpar
            
        
        obj = (atoms['consts'] | atoms['float'] | array | func_call | variable)
        atom = (
                Optional("-") + # optional unary minus
                (
                    obj.addParseAction(self.push_first) |
                    (lpar + expr.suppress() + rpar) # subexpression
               )
           ).setParseAction(self.push_unary_minus)
        
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of
        # left-to-right. That is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore(
                (expop + factor).setParseAction(self.push_first)
           )

        # sequence of multiplications
        term = factor + ZeroOrMore(
                (multop + factor).setParseAction(self.push_first)
           )
        
        # sequence of summations
        expr << term + ZeroOrMore(
                (addop + term).setParseAction(self.push_first)
           )
        
        # comparison operators
        equation = expr + \
            Optional(cmpop + expr).setParseAction(self.push_first)

        # assignment operator
        self.parser = (
                (variable ^ array).setParseAction(self.push_first) + 
                atoms['assign'] +
                equation
           ).setParseAction(self._push2stack('=')) | \
            equation

        return self.parser


    def _get_nested_structure_rec(self, s, array_list=False, func_list=False):
        """ Calculates the nested structure from the expression """
        
        # initialize values
        op = s.pop()
        array_end = False
        func_end = False
        
        # check whether we are currently in a function list
        if func_list and op == '(':
            res = None
            func_end = True

        elif array_list and op == '[':
            res = None
            array_end = True

        elif op == 'UNARY-':
            res = dict(
                op='UNARY-', pos='prefix',
                args=[ self._get_nested_structure_rec(s)[0] ]
           )
            
        #elif op == '=':
        #    res = dict(op='=', args=[self._get_nested_structure_rec(s)])
            
        elif op in "+-*/^=" or op == '==': # operators using two values
            arg2 = self._get_nested_structure_rec(s)[0]
            arg1 = self._get_nested_structure_rec(s)[0]
            
            if op == "^" and arg1 == "E": # optimization
                res = dict(op="exp", pos='prefix', args=[arg2])
            else:
                res = dict(op=op, pos='infix', args=[arg1, arg2])

        elif len(s) > 1 and s[-1] == ']': # array selector has started
            s.pop() # remove the bracket
            
            # iterate through arguments of the function
            args = []
            while True:
                val, array_finished, func_finished = \
                            self._get_nested_structure_rec(s, True, func_list)
                if array_finished:
                    break
                args.append(val)

            args.reverse()
            res = dict(op=op, pos='array', args=args)

        elif len(s) > 1 and s[-1] == ')': # function has started
            s.pop() # remove the bracket
            
            # iterate through arguments of the function
            args = []
            while True:
                val, array_finished, func_finished = \
                            self._get_nested_structure_rec(s, array_list, True)
                if func_finished:
                    break
                args.append(val)

            args.reverse()
            res = dict(op=op, pos='function', args=args)
            
        # constants and variables
        else: 
            res = op
        
        return res, array_end, func_end


    def get_nested_structure(self):
        """ Calculates the nested structure from the expression """
        
        if self.result_stack == []:
            raise ValueError('Nothing has been parsed, yet.')

        s = copy.copy(self.result_stack) # otherwise, we loose self.exprStack
        res = self._get_nested_structure_rec(s)[0]
        #if self.assignment is not None:
        #    res = { 'op':'=', 'pos':'infix', 'args':[self.assignment, res] }

        return res


    def parse_string(self, s):
        """ Parses a formula given as a string """
        # reset cache
        self.result_stack = []
        
        # process the input string
        s = self.language.pre_process(s)
        if s.strip() == '':
            self.result_parse = []
            self.result_nested = ''
        else:
            self.result_parse = self.parser.parseString(s)
            self.result_nested = self.get_nested_structure()
        
        return self.result_nested

