custom = "text"
custom2 = "concat"
my_list = [ "yes", "no", "maybe" ]
my_list2 = [ "red", "green", "blue" ]
empty_list = []

def main():
    @factory.rule
    def all(context):
        """
        all: prefix prefix_list suffix suffix_list empty_list concat concat_prelist concat_postlist concat_doublelist concat_big
        """

    @factory.rule
    def dummyRule(context):
        """
        %.dummy:
        """

    @factory.rule
    def prefix(context):
        """
        prefix: a.dummy
            echo thing1=$custom thing2=$<
        """

    @factory.rule
    def prefix_list(context):
        """
        prefix_list: a.dummy b.dummy c.dummy
            echo thing1=$[my_list] thing2=$^
        """

    @factory.rule
    def suffix(context):
        """
        suffix: a.dummy
            echo $(custom)=yes $<=no
        """

    @factory.rule
    def suffix_list(context):
        """
        suffix_list: a.dummy b.dummy c.dummy
            echo $[my_list]=yes $^=no
        """

    @factory.rule
    def empty_list(context):
        """
        empty_list:
            echo nothing -> foo-$[empty_list]-bar
        """

    @factory.rule
    def concat(context):
        """
        concat:
            echo $(custom)$(custom2)
        """

    @factory.rule
    def concat_prelist(context):
        """
        concat_prelist:
            echo $(custom)$[my_list]
        """

    @factory.rule
    def concat_postlist(context):
        """
        concat_postlist:
            echo $[my_list]$(custom)
        """

    @factory.rule
    def concat_doublelist(context):
        """
        concat_doublelist:
            echo $[my_list]$[my_list2]
        """

    @factory.rule
    def concat_big(context):
        """
        concat_big:
            echo $(custom)=$[my_list]-$(custom2)>$[my_list2]
        """

    targets = "prefix prefix_list suffix suffix_list empty_list concat concat_prelist concat_postlist concat_doublelist concat_big"
    for targ in targets.split():
        factory.AddTarget(targ)

    factory.AddTarget("a.dummy")
    factory.AddTarget("b.dummy")
    factory.AddTarget("c.dummy")

    factory.Build("all")


