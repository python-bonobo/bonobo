class token:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


begin = token('begin')
end = token('end')
