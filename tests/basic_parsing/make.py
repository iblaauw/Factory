
custom_text="This is custom text"
custom_text2="This is more custom text"
custom_list = [ "Custom", "Stuff", "In", "A", "List" ]

def main():
    @factory.rule
    def dummyRule(context):
        """
        %.dummy:
        """

    @factory.rule
    def longset(context):
        """
        longset: a.dummy b.dummy c.dummy
            echo $@ $< $^
        """

    @factory.rule
    def custom(context):
        """
        custom:
            echo $custom_text
        """

    @factory.rule
    def custom2(context):
        """
        custom2:
            echo $(custom_text2)
        """

    @factory.rule
    def customlist(context):
        """
        customlist:
            echo $[custom_list]
        """

    @factory.rule
    def allrule(context):
        """
        all: longset custom custom2 customlist
        """

    factory.AddTarget("longset")
    factory.AddTarget("a.dummy")
    factory.AddTarget("b.dummy")
    factory.AddTarget("c.dummy")
    factory.Build("all")

