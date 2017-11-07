class Token:
    """Token factory."""

    def __init__(self, name):
        self.__name__ = name
        self.__doc__ = 'The {!r} token.'.format(name)

    def __repr__(self):
        return '<{}>'.format(self.__name__)
