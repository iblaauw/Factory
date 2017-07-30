import shlex
import subprocess
from .build_dir import translate_file

class Action(object):
    def __init__(self, actionline):
        self.actionlist = shlex.split(actionline)

    def execute(self, context):
        to_exec = self._get_to_exec(context)
        print(' '.join(to_exec))
        ret_val = subprocess.call(to_exec)
        if ret_val != 0:
            raise Exception("An error occurred while executing a rule")

    def _get_to_exec(self, context):
        command_list = []
        for act in self.actionlist:
            if act.startswith("$"):
                expanded = self._expand_var(act[1:], context)
                command_list.extend(expanded)
            else:
                command_list.append(act)
        return command_list

    def _expand_var(self, var, context):
        if var == "":
            return [ '$' ]
        if var == '@':
            return [ translate_file(context.target) ]
        if var == '^':
            return [ translate_file(dep) for dep in context.dependents ]
        if var == '<':
            if len(context.dependents) == 0:
                raise Exception("Error: '$<' is not defined when no dependencies exist")
            return [ translate_file(context.dependents[0]) ]
        if var[0] == '[' and var[-1] == ']': # return as array
            subvar = var[1:-1]
            if subvar in context.context_dict:
                val = context.context_dict[subvar]
                return [ str(item) for item in val ]
        elif var in context.context_dict:
            val = str(context.context_dict[var])
            return [ val ]
        print("Warning: unrecognized variable '{}'. Ignoring it.".format(var))
        return [ '$' + var ]

    def __str__(self):
        return str(self.actionlist)



