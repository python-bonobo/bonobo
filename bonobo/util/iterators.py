class IntegerSequenceGenerator:
    """Simple integer sequence generator."""

    def __init__(self):
        self.current = 0

    def get(self):
        return self.current

    def __next__(self):
        self.current += 1
        return self.current


def force_iterator(x):
    if isinstance(x, str):
        return [x]
    try:
        return iter(x)
    except Exception as e:
        return [x] if x else []
