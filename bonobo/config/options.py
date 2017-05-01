class Option:
    """
    An Option is a descriptor for a required or optional parameter of a Configurable.
    
    """
    _creation_counter = 0

    def __init__(self, type=None, *, required=False, positional=False, default=None):
        self.name = None
        self.type = type
        self.required = required
        self.positional = positional
        self.default = default

        # This hack is necessary for python3.5
        self._creation_counter = Option._creation_counter
        Option._creation_counter += 1

    def get_default(self):
        return self.default() if callable(self.default) else self.default

    def __get__(self, inst, typ):
        if not self.name in inst.__options_values__:
            inst.__options_values__[self.name] = self.get_default()
        return inst.__options_values__[self.name]

    def __set__(self, inst, value):
        inst.__options_values__[self.name] = self.type(value) if self.type else value
