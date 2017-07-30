from . import rules
from . import main

# Flags
CXXFLAGS = []
LDFLAGS = []
CXX = "g++"


def AddCppToORule():
    rule = \
    """%.o : %.cpp
            $CXX $[CXXFLAGS] -c $^ -o $@"""
    rules.add_rule(rule)

def AddOToExeRule(target=None):
    if target is None:
        target = main.default_target
    if target is None:
        raise Exception("Error: no target specified and no default target could be found")

    rulestr = "{}: \n $CXX $[LDFLAGS] $^ -o $@".format(target)
    def capture_o_files(context):
        cpp_files = [ f[:-4] for f in main.startpoints if f.endswith(".cpp") ]
        o_files = [ f + ".o" for f in cpp_files ]
        context.dependencies.extend(o_files)

    rules.add_rule(rulestr, func=capture_o_files, modifies_dependencies=True)

def UseDefaultCppRules(target=None):
    AddCppToORule()
    AddOToExeRule(target)

