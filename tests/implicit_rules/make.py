
def main():
    factory.Add("test.cpp")
    factory.Add("test2.cpp")
    factory.AddTarget("program")

    factory.builtin_rules.UseDefaultCppRules()
    factory.builtin_rules.CXXFLAGS.append("-Wall")
    factory.builtin_rules.CXXFLAGS.append("-std=c++11")
    factory.builtin_rules.CXXFLAGS.append("-Iinclude")

    factory.Build()

    test_utils.EnsureExists("program")

    factory.Clean()

    test_utils.EnsureNotExists("program")

