
def main():

    @factory.rule
    def cppRule(context):
        """
        %.o : %.cpp
            g++ -c $< -o $@
        """

    @factory.rule
    def exeRule(context):
        """
        program : src/test.o src/test2.o
            g++ $^ -o $@
        """

    factory.AddDir("src")
    factory.Build("program")

    test_utils.EnsureExists("program")
    test_utils.EnsureExists("build/src/test.o")
    test_utils.EnsureExists("build/src/test2.o")

    factory.Clean("program")

    test_utils.EnsureNotExists("program")
    test_utils.EnsureNotExists("build/src/test.o")
    test_utils.EnsureNotExists("build/src/test2.o")

