import time


class Timer(object):
    """
    Context manager used to time execution of stuff.
    """

    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type=None, value=None, traceback=None):
        # Error handling here
        self.__finish = time.time()

    @property
    def duration(self):
        return self.__finish - self.__start

    def __str__(self):
        return str(int(self.duration * 1000) / 1000.0) + 's'
