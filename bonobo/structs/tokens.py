class Token:
    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "<{}>".format(self.__name__)


class Flag(Token):
    must_be_first = False
    must_be_last = False
    allows_data = True
