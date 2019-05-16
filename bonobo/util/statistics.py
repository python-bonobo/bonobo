import time


class WithStatistics:
    def __init__(self, *names):
        self.statistics_names = names
        self.statistics = {name: 0 for name in names}

    def get_statistics(self, *args, **kwargs):
        return ((name, self.statistics[name]) for name in self.statistics_names)

    def get_statistics_as_string(self, *args, **kwargs):
        stats = tuple("{0}={1}".format(name, cnt) for name, cnt in self.get_statistics(*args, **kwargs) if cnt > 0)
        return (kwargs.get("prefix", "") + " ".join(stats)) if len(stats) else ""

    def increment(self, name, *, amount=1):
        self.statistics[name] += amount


class Timer:
    """
    Context manager used to time execution of stuff.
    """

    def __enter__(self):
        self.__start = time.time()
        return self

    def __exit__(self, type=None, value=None, traceback=None):  # lgtm [py/special-method-wrong-signature]
        # Error handling here
        self.__finish = time.time()

    @property
    def duration(self):
        return self.__finish - self.__start

    def __str__(self):
        return str(int(self.duration * 1000) / 1000.0) + "s"
