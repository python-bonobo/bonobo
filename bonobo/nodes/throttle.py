import threading
import time

from bonobo.config import Configurable, ContextProcessor, Method, Option


class RateLimitBucket(threading.Thread):
    daemon = True

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def __init__(self, initial=1, period=1, amount=1):
        super(RateLimitBucket, self).__init__()
        self.semaphore = threading.BoundedSemaphore(initial)
        self.amount = amount
        self.period = period

        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self.stopped:
            time.sleep(self.period)
            for _ in range(self.amount):
                self.semaphore.release()

    def wait(self):
        return self.semaphore.acquire()


class RateLimited(Configurable):
    handler = Method()

    initial = Option(int, positional=True, default=1)
    period = Option(int, positional=True, default=1)
    amount = Option(int, positional=True, default=1)

    @ContextProcessor
    def bucket(self, context):
        bucket = RateLimitBucket(self.initial, self.amount, self.period)
        bucket.start()
        yield bucket
        bucket.stop()
        bucket.join()

    def __call__(self, bucket, *args, **kwargs):
        bucket.wait()
        return self.handler(*args, **kwargs)
