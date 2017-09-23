from . import matcher
from .action import Action
from .utils import get_caller_dict
import re

ruleset = []

def rule(func):
    parent_dict = get_caller_dict()
    doc = func.__doc__
    return _rule_entry(func, doc, parent_dict, False, False)
    #newrule = parse_rule(func, doc, parent_dict, False)
    #if newrule is not None:
    #    ruleset.append(newrule)
    #    return newrule

    #return func

def regex_rule(func):
    parent_dict = get_caller_dict()
    doc = func.__doc__
    return _rule_entry(func, doc, parent_dict, True, False)
    #newrule = parse_rule(func, doc, parent_dict, True)
    #if newrule is not None:
    #    ruleset.append(newrule)
    #    return newrule

    #return func

def add_rule(rulestr, func=None, modifies_dependencies=False):
    parent_dict = get_caller_dict()
    return _rule_entry(func, rulestr, parent_dict, False, modifies_dependencies)

def add_regex_rule(rulestr, func=None, modifies_dependencies=False):
    parent_dict = get_caller_dict()
    return _rule_entry(func, rulestr, parent_dict, True, modifies_dependencies)

# Helper function that starts off the rule parsing process and adds the rule to the set
def _rule_entry(func, doc, parent_dict, isregex, modify_depend):
    newrule = parse_rule(func, doc, parent_dict, isregex)
    if newrule is not None:
        ruleset.append(newrule)
        if modify_depend:
            newrule.modifies_dependencies = True
        return newrule

    return func

class Rule(object):
    def __init__(self, func, context_dict, target, dependencies, action_list):
        self.func = func
        self.context_dict = context_dict
        self.target = target
        self.dependencies = dependencies
        self.action_list = action_list
        self.modifies_dependencies = False

    def execute(self, context):
        if self.action_list is None:
            return

        if len(self.action_list) == 0:
            return

        for action in self.action_list:
            action.execute(context)

    def __str__(self):
        val = "Rule {}:\n".format(self.func.__name__)
        tabbed = "    {}\n"
        val += tabbed.format(self.target)
        val += tabbed.format(self.dependencies)
        val += tabbed.format(self.action)
        return val

    def __call__(self, *args):
        self.func(*args)


def parse_rule(func, doc, parent_dict, isregex):
    if doc is None:
        return Rule(func, parent_dict, None, None, None)

    lines = doc.splitlines()
    lines = [ l for l in lines if len(l) > 0 ]
    if len(lines) == 0:
        return Rule(func, parent_dict, None, None, None)

    line1 = lines[0].strip()
    target_depend = line1.split(':')
    if len(target_depend) != 2:
        return Rule(func, parent_dict, None, None, None)

    target_sec = target_depend[0].strip()
    depend_sec = target_depend[1].strip()

    if isregex:
        target = parse_target_regex(target_sec)
        depends = parse_depends_regex(depend_sec)
    else:
        target = parse_target(target_sec)
        depends = parse_depends(depend_sec)

    if target is None or depends is None:
        print("Warning: failed to parse rule '{}'. This rule may not work correctly".format(func.__name__))
        return Rule(func, parent_dict, None, None, None)

    if len(lines) == 1:
        return Rule(func, parent_dict, target, depends, None)

    action_list = []
    for action_line in lines[1:]:
        action_line = action_line.strip()
        action = parse_action(action_line)
        if action is not None:
            action_list.append(action)
    if len(action_list) == 0:
        return Rule(func, parent_dict, target, depends, None)
    return Rule(func, parent_dict, target, depends, action_list)


def do_escape_target(val):
    replacement = "(.*)"
    escaped = re.escape(val)
    start = 0
    result = ""
    while True:
        index = escaped.find("\\%", start)
        if index == -1:
            result += escaped
            break

        result += escaped[:index]
        escaped = escaped[index:]

        if len(escaped) > 3 and escaped[2] == '\\' and escaped[3] == '%':
            # double percents is escaped: %% -> %
            result += "\\%"
            escaped = escaped[4:]
        else:
            # single percent is replaced: % -> replacement
            result += replacement
            escaped = escaped[2:]

    return result

def do_escape_dependent(val):
    count = 1
    escaped = val
    start = 0
    result = ""
    while True:
        index = escaped.find("%", start)
        if index == -1:
            result += escaped
            break

        result += escaped[:index]
        escaped = escaped[index:]

        if len(escaped) > 1 and escaped[1] == '%':
            # double percents is escaped: %% -> %
            result += "%"
            escaped = escaped[2:]
        else:
            # single percent is replaced: % -> replacement
            result += "\\{}".format(count)
            count += 1
            escaped = escaped[1:]

    return result


def parse_target(section):
    if len(section.split()) > 1:
        return None
    if section == "":
        return None

    result = do_escape_target(section)

    return matcher.TargetMatcher(result)

def parse_depends(section):
    depends = section.split()
    results = []
    for dep in depends:
        index = 1
        result = do_escape_dependent(dep)
        results.append(result)

    return matcher.DependentMatcher(results)

def parse_target_regex(section):
    if len(section.split()) > 1:
        return None
    if section == "":
        return None

    return matcher.TargetMatcher(section)

def parse_depends_regex(section):
    return matcher.DependentMatcher(section.split())

def parse_action(line):
    if line is None:
        return None
    if line == "":
        return None
    return Action(line)

def ResetRules():
    ruleset.clear()

