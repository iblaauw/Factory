import shlex
import subprocess
from .build_dir import translate_file

class Action(object):
    def __init__(self, actionline):
        split = shlex.split(actionline)
        self.parsers = [ _VarParser(piece) for piece in split ]
        #print("*** " + actionline + " ***")
        #for p in self.parsers:
        #    print(p)

    def execute(self, context):
        to_exec =  list(self._expand(context))
        print(' '.join(to_exec))
        ret_val = subprocess.call(to_exec)
        if ret_val != 0:
            raise Exception("An error occurred while executing a rule")

    def _expand(self, context):
        for parser in self.parsers:
            expanded = parser.CreateExpander().Expand(context)
            for item in expanded:
                yield item

    def __str__(self):
        return str(self.expander)

def _ExpandVar(var, is_list, context):
    if var == '$':
        # $$ => $
        return [ '$' ]
    if var == '@':
        return [ translate_file(context.target) ]
    if var == '^':
        return [ translate_file(dep) for dep in context.dependencies ]
    if var == '<':
        if len(context.dependencies) == 0:
            raise Exception("Error: '$<' is not defined when no dependencies exist")
        return [ translate_file(context.dependencies[0]) ]
    if is_list:
        if var in context.context_dict:
            val = context.context_dict[var]
            return [ str(item) for item in val ]
    elif var in context.context_dict:
        val = str(context.context_dict[var])
        return [ val ]
    print("Warning: unrecognized variable '{}'. Ignoring it.".format(var))
    return [ var ]


#class _VarExpander(object):
#    _SpecialChars = [ '@', '^', '<', '$' ]
#    _BracketPairs = { '[' : ']', '(' : ')' }
#    def __init__(self, action_line):
#        self.result = []
#        self.var_data = []
#
#        action_list = shlex.split(action_line)
#        self._Preparse(action_list)
#
#    def _Preparse(self, action_list):
#        # The goal here is to extract the indices of all $ # and record where they are
#        # as well as what type of variable it should be
#        # This should be called on rule create to help badly formed rules to fail early
#        for item in action_list:
#            parsed = self._DoPreparse(item)
#            self.result.append(parsed)
#
#    def _DoPreparse(self, item):
#        index = item.find('$')
#        if index == -1:
#            return item
#
#        left_side = item[:index]
#        right_side = item[index+1:]
#
#        if len(right_side) == 0:
#            return item
#
#        data = _Bag()
#        data.result_index = len(self.result)
#        data.char_index = index
#        data.bracket_type = '(' # Normal
#
#        first_char = right_side[0]
#
#        if first_char in _VarExpander._BracketPairs:
#            # Parse bracketed ones such as $(myvar) or $[myvar]
#            close_bracket = _VarExpander._BracketPairs[first_char]
#            bracket_index = right_side.find(close_bracket)
#            if bracket_index == -1:
#                raise Exception("Error parsing rule. Expected a closing '{}' in rule piece '{}'".format(close_bracket, item))
#
#            data.var = right_side[1:bracket_index]
#            data.bracket_type = first_char
#
#            right_side = right_side[bracket_index+1:]
#        elif first_char in _VarExpander._SpecialChars:
#            # Parse special builtin vars like $@, $<, $^, etc
#            data.var = first_char
#            right_side = right_side[1:]
#        else:
#            # Parse any other variables
#            data.var = right_side
#            right_side = ""
#
#        # TODO: Validate data.var here?
#        self.var_data.append(data)
#
#        if len(right_side) > 0:
#            left_side += self._DoPreparse(right_side)
#
#        return left_side
#
#    def Expand(self, context):
#        expanded = []
#        for i in range(len(self.result)):
#            expanded += self._DoExpand(i, context)
#        return expanded
#
#    def _DoExpand(self, result_index, context):
#        result_piece = self.result[result_index]
#        if len(self.var_data) == 0:
#            return [ result_piece ]
#
#        return self._RecurseExpand(self.var_data, result_piece, result_index, context)
#
#
#    def _RecurseExpand(self, var_data, result_piece, index, context):
#        assert(len(var_data) > 0)
#
#        print("DATA: {}".format(var_data))
#        data = var_data[0]
#        if data.result_index != index:
#            print("Quick return")
#            return [ result_piece ]
#
#        var_data = var_data[1:]
#
#        # Split the string in 2
#        left_side = result_piece[:data.char_index]
#        right_side = result_piece[data.char_index:]
#
#        # expand the variable
#        is_list = data.bracket_type == '['
#        var = _ExpandVar(data.var, is_list, context)
#
#        # combine the variable expansion with the left side
#        if len(left_side) == 0:
#            left_complete = var
#        else:
#            left_complete = [ left_side + piece for piece in var ]
#
#        # expand the right side (may have to recurse)
#        if len(var_data) == 0:
#            right_expanded = [ right_side ]
#        else:
#            right_expanded = self._RecurseExpand(var_data, right_side, index, context) # recurse!
#
#        # combine the combined left with the expanded right
#        complete = []
#        for l in left_complete:
#            for r in right_expanded:
#                complete.append(l + r)
#
#        return complete
#
#
#    def __str__(self):
#        return ' '.join(self.result)

class WorkingString(object):
    def __init__(self, line):
        self.full_line = line
        self.line = line
        self.result = ""
        self.index = 0

    def __getitem__(self, index):
        return self.line[index]

    def discard(self, amount):
        substr = self.line[:amount]
        self.line = self.line[amount:]
        self.index += amount
        return substr

    def discard_all(self):
        line = self.line
        self.index += len(self.line)
        self.line = ''
        return line

    def keep(self, amount):
        self.result += self.discard(amount)

    def keep_all(self):
        self.result += self.discard_all()

    def add(self, new_str):
        self.result += new_str

    def find(self, thing):
        return self.line.find(thing)

    def find_whitespace(self):
        index = self.find(' ')
        if index == -1:
            index = self.find('\t')
        return index

    def empty(self):
        return len(self.line) == 0

    def get_result(self):
        return self.result

    def get_index(self):
        return self.index

    def get_remaining(self):
        return self.line

    def copy(self):
        duplicate = WorkingString('')
        self.full_line   = self.full_line
        self.line        = self.line
        self.result      = self.result
        self.index       = self.index
        return duplicate

class _VarParser(object):
    _SpecialChars = [ '@', '^', '<', '$' ]
    _BracketPairs = { '[' : ']', '(' : ')' }

    def __init__(self, action_line):
        self.full_line = action_line
        self.result = ''
        self.parse_data = []

        self._DoParse(action_line)

    def _DoParse(self, action_line):
        line = WorkingString(action_line)

        while not line.empty():
            dollar_index = line.find('$')

            if dollar_index == -1:
                line.keep_all()
                break

            line.keep(dollar_index)
            line.discard(1) # throw out the '$'

            if line.empty():
                raise Exception("Invalid syntax: expected variable name after '$'")

            var_data = _Bag()
            var_data.index = len(line.get_result())
            var_data.bracket = None

            if line[0] in _VarParser._SpecialChars:
                var_data.var = line.discard(1)
            elif line[0] in _VarParser._BracketPairs:
                open_bracket = line[0]
                close_bracket = _VarParser._BracketPairs[open_bracket]

                line.discard(1)
                close_index = line.find(close_bracket)

                if close_index == -1:
                    raise Exception("Invalid syntax: could not find closing '{}' to match '{}'".format(close_bracket, open_bracket))

                var_data.bracket = open_bracket
                var_data.var = line.discard(close_index)
                line.discard(1) # also throw out the close bracket
            else:
                space_index = line.find_whitespace()
                if space_index == -1:
                    var_data.var = line.discard_all()
                else:
                    var_data.var = line.discard(space_index)

            self.parse_data.append(var_data)

        self.result = line.get_result()

    def CreateExpander(self):
        return _VarExpander(self.result, self.parse_data)

    def __str__(self):
        result = "{} -> {} ::".format(self.full_line, self.result)
        for d in self.parse_data:
            result += " ({},{},{})".format(d.var, d.index, d.bracket)

        return result

class _VarExpander(object):
    def __init__(self, input_str, parse_data):
        self.line = input_str
        self.parse_data = list(parse_data)
        self.result_data = []

    def Expand(self, context):
        line = WorkingString(self.line)
        return self._RecurseExpand(line, self.parse_data, context)

    def _RecurseExpand(self, line, data, context):
        if len(data) == 0:
            line.keep_all()
            return [ line.get_result() ]

        var_data = data[0]
        data = data[1:]

        line.keep(var_data.index - line.get_index())

        list_result = var_data.bracket == '['
        var_results_all = _ExpandVar(var_data.var, list_result, context)

        to_return = []
        for var_result in var_results_all:
            new_line = line.copy() 
            new_line.add(var_result)
            recurse_results = self._RecurseExpand(new_line, data, context)

            for r in recurse_results:
                to_return.append(r)

        return to_return


class _Bag(object):
    pass


