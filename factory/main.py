import os
import sys
from collections import namedtuple
from .rules import ruleset, ResetRules
from .utils import modify_time
from .build_dir import known_files, translate_file, ResetFiles
from .special_target import special_target_dict, ResetSpecial

startpoints = set() # The set of files that already exist before building happens
                    # These will not be removed on clean, and will stop any rule matching recursion

default_target = None # The default target to build, if none is specified

BuildContext = namedtuple('BuildContext', 'target dependencies context_dict')

def Execute(args=None):
    action = Build
    if args is None:
        args = sys.argv[1:]
    if len(args) == 0:
        target = None
    else:
        target = args[0]
        if target.lower() in special_target_dict:
            action = special_target_dict[target.lower()]
            target = args[1] if len(args) > 1 else None

    if target is None:
        target = default_target
    action(target)

def Build(target=None):
    if target is None:
        if default_target is None:
            raise Exception("No target specified and no default target found")
        target = default_target
    known_files.add(target)
    _doBuild(target)
    print("Success!")

def Add(startpoint):
    startpoints.add(startpoint)
    known_files.add(startpoint)

def AddDir(directory, recurse=False):
    files = (f for f in os.listdir(directory) if os.isfile(f))
    for f in files:
        Add(f)

    if recurse:
        dirs = (d for d in os.listdir(directory) if os.isdir(d))
        for d in dirs:
            AddDir(d)

def AddTarget(target):
    known_files.add(target)
    global default_target
    if default_target is None:
        default_target = target

def Clean(target=None):
    if target is None:
        if default_target is None:
            raise Exception("No target specified and no default target found")
        target = default_target
    known_files.add(target)
    _doClean(target)
    print("Success!")
special_target_dict["clean"] = Clean

def _doBuild(target):
    if target in startpoints: # No need to build a startpoint
        return

    rule, data = _findRule(target)
    depends = rule.dependencies.expand(data)

    context = BuildContext(target, depends, rule.context_dict)

    if rule.func is not None:
        if rule.modifies_dependencies:
            rule.func(context)

    for dep in context.dependencies:
        _doBuild(dep)

    real_target = translate_file(context.target)
    real_deps = (translate_file(dep) for dep in context.dependencies)

    mtime = modify_time(real_target)

    build_needed = mtime == -1 or len(depends) == 0
    if not build_needed:
        build_needed = any(modify_time(dep) > mtime for dep in real_deps)

    if build_needed:
        # execute
        if rule.func is not None:
            if not rule.modifies_dependencies: # Already been called in that case
                rule.func(context)
                # TODO: dynamically determine what to pass based on number of parameters to 'rule.func'

        if rule.action is not None:
            rule.action.execute(context)


def _findRule(name):
    data = None
    matching_rule = None
    for rule in ruleset:
        result = rule.target.trymatch(name)
        if result is not None:
            if matching_rule is not None:
                raise Exception("Error: the item '{}' is ambiguous, multiple rules apply".format(name))
            data = result
            matching_rule = rule

    if matching_rule is None:
        raise Exception("Error: no rule found for item '{}'".format(name))

    return (matching_rule, data)

def _doClean(target):
    if target in startpoints: # don't remove startpoints
        return

    rule, data = _findRule(target)
    depends = rule.dependencies.expand(data)

    context = BuildContext(target, depends, rule.context_dict)

    if rule.func is not None:
        if rule.modifies_dependencies:
            rule.func(context)

    for dep in context.dependencies:
        _doClean(dep)

    real = translate_file(target)
    if os.path.exists(real):
        print("rm {}".format(real))
        os.remove(real)

def Reset():
    ResetRules()
    ResetFiles()
    ResetSpecial()

    startpoints.clear()

    global default_target
    default_target = None

