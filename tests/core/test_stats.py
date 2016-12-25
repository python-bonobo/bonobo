from bonobo.core.stats import WithStatistics


class MyThingWithStats(WithStatistics):
    def get_stats(self, *args, **kwargs):
        return (
            ('foo', 42),
            ('bar', 69), )


def test_with_statistics():
    o = MyThingWithStats()
    assert o.get_stats_as_string() == 'foo=42 bar=69'
