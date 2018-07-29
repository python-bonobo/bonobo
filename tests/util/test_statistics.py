from bonobo.util.statistics import WithStatistics


class MyThingWithStats(WithStatistics):
    def get_statistics(self, *args, **kwargs):
        return (("foo", 42), ("bar", 69))


def test_with_statistics():
    o = MyThingWithStats()
    assert o.get_statistics_as_string() == "foo=42 bar=69"
