""" This file defines the supported languages for both parsing and writing """

import re
from pyparsing import (
    Literal,
    CaselessLiteral,
    Word,
    Combine,
    Optional,
    nums,
    alphas,
    upcaseTokens,
    replaceWith,
    Keyword,
    CaselessKeyword,
)


def appendString(appendage):
    """Returns a function suitable for a parseAction which appends the current
    token with the given string `appendage`"""
    return lambda strg, loc, toks: toks[0] + appendage


class LanguageBase(object):
    """Base class defining a generic language.
    Derive from this class to make include your own language"""

    lpar = "("
    rpar = ")"
    func_lpar = "("
    func_delim = ","
    func_rpar = ")"
    array_lpar = "["
    array_delim = ","
    array_rpar = "]"

    op_assign = "="

    eol = "\n"  # end of line

    replacements = {}
    operators = {}

    def get_parser_atoms(self):
        """ Function defining the atoms of the grammar """

        point = Literal(".")
        e = CaselessLiteral("E")
        return {
            # float number:
            "int": Combine(Word("+-" + nums, nums)),
            "float": Combine(
                Word("+-" + nums, nums)
                + Optional(point + Optional(Word(nums)))
                + Optional(e + Word("+-" + nums, nums))
            ),
            "variable": Word(alphas, alphas + nums + "_"),
            "array_lpar": Literal(self.array_lpar),
            "array_delim": Literal(self.array_delim),
            "array_rpar": Literal(self.array_rpar),
            "function": Word(alphas, alphas + nums + "_$"),
            "func_lpar": Literal(self.func_lpar),
            "func_delim": Literal(self.func_delim),
            "func_rpar": Literal(self.func_rpar),
            "assign": Literal(self.op_assign),
            "equal": Literal("=="),
            "plus": Literal("+"),
            "minus": Literal("-"),
            "mult": Literal("*"),
            "div": Literal("/"),
            "lpar": Literal(self.lpar),
            "rpar": Literal(self.rpar),
            "exp": Literal("^"),
            "consts": CaselessKeyword("PI").setParseAction(upcaseTokens)
            | CaselessKeyword("E").setParseAction(upcaseTokens),
        }

    def format_atom(self, s):
        """Function which might possibly be used to format a part of an
        expression"""
        return str(s)

    def pre_process(self, s):
        """ Function used to pre_process an input string """
        return s


class LanguagePython(LanguageBase):
    """Language class with the settings for the python language.
    The mathematical functions and constants are prepended with an `np.` for
    convenience with numpy usage.
    """

    replacements = {
        "PI": "np.pi",
        "E": "np.e",
    }
    operators = {
        "^": "**",
        "UNARY-": "-",
        "sign": "np.sign",
        "sin": "np.sin",
        "cos": "np.cos",
        "tan": "np.tan",
        "arcsin": "np.asin",
        "arccos": "np.acos",
        "arctan": "np.atan",
        "sinh": "np.sinh",
        "cosh": "np.cosh",
        "tanh": "np.tanh",
        "exp": "np.exp",
        "ln": "np.log",
        "sqrt": "np.sqrt",
        "trunc": "np.trunc",
        "sphericalharmonic": "sph_harm",
        "expintegrale": "scipy.special.expn",
        "gamma": "gamma",
    }

    def __init__(self, int2float=False):
        super(LanguagePython, self).__init__()
        self.int2float = int2float
        # regular expression for detecting integers
        self.pattern_int = re.compile("^[+-]?\d+$")

    def get_parser_atoms(self):
        """ Function defining the atoms of the grammar """
        atoms = super(LanguagePython, self).get_parser_atoms()
        atoms["exp"] = Literal("**").setParseAction(replaceWith("^"))
        atoms["consts"] = Keyword("np.pi").setParseAction(replaceWith("PI")) | Keyword(
            "np.e"
        ).setParseAction(replaceWith("E"))

        if self.int2float:
            point = Literal(".")
            e = CaselessKeyword("E")
            atoms["float"] = Word("+-" + nums, nums).setParseAction(
                appendString(".")
            ) | Combine(
                Word("+-" + nums, nums)
                + Optional(point + Optional(Word(nums)))
                + Optional(e + Word("+-" + nums, nums))
            )

        return atoms

    def format_atom(self, s):
        if self.int2float and self.pattern_int.match(s):
            return s + "."
        else:
            return self.replacements.get(s, str(s))


class LanguageMathematica(LanguageBase):
    """ Parser for  Mathematica style formulas """

    func_lpar = "["
    func_delim = ", "
    func_rpar = "]"
    array_lpar = "[["
    array_rpar = "]]"

    replacements = {
        "PI": "Pi",
        "E": "E",
    }
    operators = {
        "^": "^",
        "UNARY-": "-",
        "sign": "Sign",
        "sin": "Sin",
        "cos": "Cos",
        "tan": "Tan",
        "arcsin": "ArcSin",
        "arccos": "ArcCos",
        "arctan": "ArcTan",
        "coth": "Coth",
        "exp": "Exp",
        "ln": "Log",
        "sqrt": "Sqrt",
        "trunc": "Trunc",
        "sphericalharmonic": "SphericalHarmonicY",
        "expintegrale": "ExpIntegralE",
        "gamma": "Gamma",
    }

    def get_parser_atoms(self):
        """ Function defining the atoms of the grammar """
        atoms = super(LanguageMathematica, self).get_parser_atoms()
        atoms["assign"] = Literal("=") | Literal(":=") | Literal("==")
        atoms["consts"] = Keyword("Pi").setParseAction(replaceWith("PI")) | Keyword(
            "E"
        ).setParseAction(replaceWith("E"))
        return atoms

    def format_atom(self, s):
        return self.replacements.get(s, str(s))

    def pre_process(self, s):
        # replace capital symbols
        s = re.sub(r"\\\[Capital(\w+)\]", r"\1", s)
        # replace remaining symbols
        s = re.sub(r"\\\[(\w+)\]", lambda m: m.group(1).lower(), s)
        return s
