import shlex
import subprocess
from .build_dir import translate_file

class Action(object):
    def __init__(self, actionline):
        self.expander = _VarExpander(actionline)

    def execute(self, context):
        to_exec = self.expander.Expand(context)
        print(' '.join(to_exec))
        ret_val = subprocess.call(to_exec)
        if ret_val != 0:
            raise Exception("An error occurred while executing a rule")

    def __str__(self):
        return str(self.expander)


class _VarExpander(object):
    _SpecialChars = [ '@', '^', '<', '$' ]
    _BracketPairs = { '[' : ']', '(' : ')' }
    def __init__(self, action_line):
        self.result = []
        self.var_data = []

        action_list = shlex.split(action_line)
        self._Preparse(action_list)

    def _Preparse(self, action_list):
        # The goal here is to extract the indices of all $ # and record where they are
        # as well as what type of variable it should be
        # This should be called on rule create to help badly formed rules to fail early
        for item in action_list:
            parsed = self._DoPreparse(item)
            self.result.append(parsed)

    def _DoPreparse(self, item):
        index = item.find('$')
        if index == -1:
            return item

        left_side = item[:index]
        right_side = item[index+1:]

        if len(right_side) == 0:
            return item

        data = _Bag()
        data.result_index = len(self.result)
        data.char_index = index
        data.bracket_type = '(' # Normal

        first_char = right_side[0]

        if first_char in _VarExpander._BracketPairs:
            # Parse bracketed ones such as $(myvar) or $[myvar]
            close_bracket = _VarExpander._BracketPairs[first_char]
            bracket_index = right_side.find(close_bracket)
            if bracket_index == -1:
                raise Exception("Error parsing rule. Expected a closing '{}' in rule piece '{}'".format(close_bracket, item))

            data.var = right_side[1:bracket_index]
            data.bracket_type = first_char

            right_side = right_side[bracket_index+1:]
        elif first_char in _VarExpander._SpecialChars:
            # Parse special builtin vars like $@, $<, $^, etc
            data.var = first_char
            right_side = right_side[1:]
        else:
            # Parse any other variables
            data.var = right_side
            right_side = ""

        # TODO: Validate data.var here?
        self.var_data.append(data)

        if len(right_side) > 0:
            left_side += self._DoPreparse(right_side)

        return left_side

    def Expand(self, context):
        expanded = []
        for i in range(len(self.result)):
            expanded += self._DoExpand(i, context)
        return expanded

    def _DoExpand(self, result_index, context):
        result_piece = self.result[result_index]
        if len(self.var_data) == 0:
            return [ result_piece ]

        return self._RecurseExpand(result_piece, result_index, context)


    def _RecurseExpand(self, result_piece, index, context):
        assert(len(self.var_data) > 0)

        data = self.var_data[0]
        if data.result_index != index:
            return [ result_piece ]

        self.var_data = self.var_data[1:]

        # Split the string in 2
        left_side = result_piece[:data.char_index]
        right_side = result_piece[data.char_index:]

        # expand the variable
        is_list = data.bracket_type == '['
        var = self._ExpandVar(data.var, is_list, context)

        # combine the variable expansion with the left side
        if len(left_side) == 0:
            left_complete = var
        else:
            left_complete = [ left_side + piece for piece in var ]

        # expand the right side (may have to recurse)
        if len(self.var_data) == 0:
            right_expanded = [ right_side ]
        else:
            right_expanded = self._RecurseExpand(right_side, index, context) # recurse!

        # combine the combined left with the expanded right
        complete = []
        for l in left_complete:
            for r in right_expanded:
                complete.append(l + r)

        return complete

    def _ExpandVar(self, var, is_list, context):
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

    def __str__(self):
        return ' '.join(self.result)


class _Bag(object):
    pass


