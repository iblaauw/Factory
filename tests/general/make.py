
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
        program : test.o
            g++ $^ -o $@
        """

    factory.Add("test.cpp")
    factory.Build("program")

    test_utils.EnsureExists("program")
    test_utils.EnsureExists("build/test.o")

    factory.Clean("program")

    test_utils.EnsureNotExists("program")
    test_utils.EnsureNotExists("build/test.o")

