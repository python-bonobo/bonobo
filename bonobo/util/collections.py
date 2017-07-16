import bisect


class sortedlist(list):
    def insort(self, x):
        bisect.insort(self, x)