
def main():

    @factory.rule
    def echoRule(context):
        """
        runit : 
            echo hello
            echo world
        """

    factory.Build("runit")


