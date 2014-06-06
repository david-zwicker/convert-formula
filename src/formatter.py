""" Defines classes which can convert the parsed formula into the style of a
certain language """

from parser_line import ParserLine
from parser_text import ParserText
from language import LanguageBase


def _operator_associative(token, a_id=0):
    """ Checks whether the operator of argument 'a_id' in the current token
    is of the same associative kind and brakets may therefore be dropped """
    
    if isinstance(token['args'][a_id], dict):
        if (token['op'] == "+" and token['args'][a_id]['op'] == "+") or \
           (token['op'] == "*" and token['args'][a_id]['op'] == "*"):
            return True
    return False


def _strip_par(s):
    """ Strips surrounding parentheses from the expression string 's' """
    if s[0] == '(':
        return s[1:-1].strip()
    else:
        return s.strip()


class Formatter(object):
    """ Base formatter class """

    def __init__(self, language):
        """ Constructor """
        if isinstance(language, LanguageBase):
            self.lang = language
        else:
            raise ValueError('`language` is not of type LanguageBase')


    def _convert_to_string_rec(self, token):
        """ Converts a token into their string representation """

        if isinstance(token, dict):

            # get the operator, which must always be defined
            op = self.lang.operators.get(token['op'], token['op'])

            if token['pos'] == 'function': # operator is a function
                args = (_strip_par(self._convert_to_string_rec(t))
                            for t in token['args'])
                s = "%s%s%s%s" % (op, self.lang.func_lpar,
                                    self.lang.func_delim.join(args),
                                    self.lang.func_rpar)

            elif token['pos'] == 'array': # operator is an array
                args = (_strip_par(self._convert_to_string_rec(t))
                            for t in token['args'])
                s = "%s%s%s%s" % (op, self.lang.array_lpar,
                                    self.lang.array_delim.join(args),
                                    self.lang.array_rpar)

            elif token['pos'] == 'infix': # operator must have two arguments
                arg1 = self._convert_to_string_rec(token['args'][0])
                arg2 = self._convert_to_string_rec(token['args'][1])

                # brackets may be dropped for associative operators
                if _operator_associative(token, 0):
                    arg1 = _strip_par(arg1)
                if _operator_associative(token, 1) \
                        or token['op'] == '=':
                    arg2 = _strip_par(arg2)
                
                s = "%s%s %s %s%s" % \
                            (self.lang.lpar, arg1, op, arg2, self.lang.rpar)
            
            # operator has exactly one argument
            elif token['pos'] == 'prefix':
                arg = self._convert_to_string_rec(token['args'][0])
                if token['op'] == 'UNARY-':
                    s = "%s%s " % (op, arg)
                else:
                    s = "%s%s%s%s " % (op, self.lang.func_lpar,
                                        _strip_par(arg), self.lang.func_rpar)
            else:
                raise ValueError(
                            'Unknown operator positions: `%s`' % token['pos'])
                
        else:
            s = self.lang.format_atom(token)
            #s = self.lang.replacements.get(token, str(token))
        
        return s.strip()


    def convert_to_string(self, token):
        """ Converts token into their string representation """
        return _strip_par(self._convert_to_string_rec(token))
    

    def __call__(self, code):
        """ Converts a completely parsed code """

        # Parser object for many lines
        if isinstance(code, ParserText):
            res = self.__call__(code.result)

        # Parser object for one line
        elif isinstance(code, ParserLine):
            res = self.convert_to_string(code.result_nested)
            
        # Dictionary structure of token
        elif isinstance(code, dict):
            res = self.convert_to_string(code)
        
        # List of any of the above
        elif hasattr(code, '__iter__'):
            res = [self.__call__(token) for token in code]
            res = self.lang.eol.join(res)
          
        # remaining type (possibly a string already)  
        else:
            res = self.convert_to_string(code)

        return res
