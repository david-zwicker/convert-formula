""" Defines a class for parsing possibly many lines of code. The class also
supports some optimizations on the expression tree, where common subexpressions
are calculated once and stored in a temporary variable.
"""

from .parser_line import ParserLine

from collections import defaultdict
import copy


class ParserText(object):
    """ Class for parsing many formulas given on multiple lines """

    default_cost = 10.0  # < default cost for unknown functions
    costs = {
        "UNARY-": 0.0,
        "array": 0.0,
        "-": 1.0,
        "+": 1.0,
        "*": 1.0,
        "/": 2.0,
        "^": 5.0,
        "=": 2.0,
        "exp": 3.0,
    }  # < costs for known operations
    optimize_threshold = 5.0  # < least saving to actually perform an optimization
    temp_var = "t_%d"  # < name of the temporary variables used for optimization

    def __init__(self, language):

        # initialize parser
        self.result = []
        self.parser = ParserLine(language)

        # iterator counting the number of temporary variables
        self.temp_count = 0
        # used for looking for variables
        self.temp_pattern = None

    def parse_text(self, text):
        """Parses many formulas given as individual lines and returns a list
        of the tokens"""

        self.result = []
        for s in text.split("\n"):
            if s != "" and not s.isspace():
                self.parser.parse_string(s)
                self.result.append(self.parser.get_nested_structure())

        return self.result

    def _calculate_costs_rec(self, token):
        """ Calculates the cost and the hash of each subexpression """

        if isinstance(token, dict):

            if token["pos"] == "array":
                token_cost = self.costs.get(token["pos"], self.default_cost)
            else:
                token_cost = self.costs.get(token["op"], self.default_cost)
            token_hash = str(hash(token["op"]))

            args = []
            for t in token["args"]:
                t, dc, dh = self._calculate_costs_rec(t)
                args.append(t)
                token_cost += dc
                token_hash += str(dh)

            token["args"] = args
            token["cost"] = token_cost
            token["hash"] = hash(token_hash)

        else:
            token_cost = 0.0
            token_hash = hash(token)

        return token, token_cost, token_hash

    def _annotate_expression(self, lines):
        """ Calculates the cost and the hash of all expressions """

        cost = 0.0
        lines_annotated = []
        for line in lines:
            res, dc, _ = self._calculate_costs_rec(line)
            lines_annotated.append(res)
            cost += dc

        return lines_annotated, cost

    def get_cost(self, lines=None):
        """ Calculates the cost and the hash of all expressions """
        if lines is None:
            self.result, cost = self._annotate_expression(self.result)
        else:
            cost = self._annotate_expression(lines)[1]
        return cost

    def _costs_subexpressions_rec(self, token, costs, counter):
        """ Sums up the cost of common subexpressions recursively """

        if isinstance(token, dict):
            costs[token["hash"]] += token["cost"]
            counter[token["hash"]] += 1

            for t in token["args"]:
                costs, counter = self._costs_subexpressions_rec(t, costs, counter)

        return costs, counter

    def _costs_subexpressions(self, lines):
        """ Compiles a list of all common subexpressions """

        # initialize the counters
        costs = defaultdict(float)
        counter = defaultdict(int)

        # accumulate costs and counts of all subexpressiosn
        for line in lines:
            costs, counter = self._costs_subexpressions_rec(line, costs, counter)

        # remove all subexpressions which only occur once
        for hash_id, count in counter.items():
            if count < 2:
                del costs[hash_id]

        return costs

    def _replace_subexpressions(self, token, hash_replace, hash_token, replacement):
        """Replaces the subexpression with the hash `hash_replace` in the
        expression tree `token` with the expression `replacement`. It
        additionally returns the replaced token as `hash_token`."""

        replaced = False
        if isinstance(token, dict):
            if token["hash"] == hash_replace:
                return replacement, token, True

            else:
                args = []
                for t in token["args"]:
                    t, hash_token, replaced_one = self._replace_subexpressions(
                        t, hash_replace, hash_token, replacement
                    )
                    if replaced_one:
                        replaced = True
                    args.append(t)
                token["args"] = args

        return token, hash_token, replaced

    def _optimize_once(self, lines):
        """Tries to find a common subexpression which migth be put in front
        of the formula definition"""

        lines, cost = self._annotate_expression(lines)
        if cost < self.optimize_threshold:
            return lines, 0.0

        # build a hash map with possible savings
        costs = self._costs_subexpressions(lines)
        if len(costs) == 0:
            return lines, 0.0

        # find the hash with the maximum saving
        hash_replace = max(costs, key=costs.get)
        if costs[hash_replace] - self.costs["="] < self.optimize_threshold:
            return lines, 0.0

        # find the dictionaries with the respective hash and replace them by
        temp_var = self.temp_var % self.temp_count

        # replace all the tokens
        res = []
        hash_token = None
        first_line = False
        for line in lines:
            line_res, hash_token, replaced = self._replace_subexpressions(
                line, hash_replace, hash_token, temp_var
            )
            if first_line is False and replaced:
                first_line = len(res)
            res.append(line_res)

        # add a line defining the temporary variable one line before the the
        # first one which uses it
        res.insert(
            first_line, {"op": "=", "pos": "infix", "args": [temp_var, hash_token]}
        )
        res, cost_new = self._annotate_expression(res)
        return res, cost - cost_new

    def optimize_runtime(self):
        """Optimizes the list of formulas by calculating subexpressions and
        assigning them to temporary variables"""

        # prepare optimization
        self.temp_count = 0
        lines = copy.copy(self.result)

        # do the optimization iteration
        while True:
            lines_new, savings = self._optimize_once(copy.deepcopy(lines))
            if savings > self.optimize_threshold:
                self.temp_count += 1
                lines = lines_new
            else:
                break

        self.result = lines
        return self.result
