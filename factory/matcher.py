import re

class TargetMatcher(object):
    def __init__(self, regexval):
        if regexval is None:
            raise TypeError("Argument cannot be None")
        self.rawregex = regexval
        self.regexval = re.compile(regexval)

    def trymatch(self, val):
        return self.regexval.fullmatch(val)

    def __str__(self):
        return self.rawregex

class DependentMatcher(object):
    def __init__(self, dependvals):
        if dependvals is None:
            raise TypeError("Argument cannot be None")
        self.dependvals = dependvals

    def expand(self, match):
        return [ match.expand(dep) for dep in self.dependvals ]

    def __str__(self):
        return str(self.dependvals)
