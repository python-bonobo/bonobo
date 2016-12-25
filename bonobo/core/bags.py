class Bag:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def apply(self, f, *args, **kwargs):
        return f(*args, *self.args, **kwargs, **self.kwargs)

    def __repr__(self):
        return '<{} *{} **{}>'.format(type(self).__name__, self.args, self.kwargs)


class Inherit(Bag):
    def override(self, input):
        self.args = input.args + self.args
        kwargs = dict(input.kwargs)
        kwargs.update(self.kwargs)
        self.kwargs = kwargs
        return self
