from . import matcher
from .action import Action
from .utils import get_caller_dict
import re

ruleset = []

def rule(func):
    parent_dict = get_caller_dict()
    newrule = parse_rule(func, parent_dict, False)
    if newrule is not None:
        ruleset.append(newrule)

    return func

def regex_rule(func):
    parent_dict = get_caller_dict()
    newrule = parse_rule(func, parent_dict, True)
    if newrule is not None:
        ruleset.append(newrule)

    return func

class Rule(object):
    def __init__(self, func, context_dict, target, dependencies, action):
        self.func = func
        self.context_dict = context_dict
        self.target = target
        self.dependencies = dependencies
        self.action = action

    def __str__(self):
        val = "Rule {}:\n".format(self.func.__name__)
        tabbed = "    {}\n"
        val += tabbed.format(self.target)
        val += tabbed.format(self.dependencies)
        val += tabbed.format(self.action)
        return val

def parse_rule(func, parent_dict, isregex):
    doc = func.__doc__
    if doc is None:
        return Rule(func, parent_dict, None, None, None)

    lines = doc.splitlines()
    lines = [ l for l in lines if len(l) > 0 ]
    if len(lines) == 0:
        return Rule(func, None, None, None)

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

    action_line = lines[1].strip()
    action = parse_action(action_line)
    if action is None:
        return Rule(func, parent_dict, target, depends, None)
    return Rule(func, parent_dict, target, depends, action)


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

