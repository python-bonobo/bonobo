""" Iterator utilities. """


def force_iterator(mixed):
    """Sudo make me an iterator.

    Deprecated?

    :param mixed:
    :return: Iterator, baby.
    """
    if isinstance(mixed, str):
        return [mixed]
    try:
        return iter(mixed)
    except TypeError:
        return [mixed] if mixed else []


def ensure_tuple(tuple_or_mixed):
    if isinstance(tuple_or_mixed, tuple):
        return tuple_or_mixed
    return (tuple_or_mixed, )


def iter_if_not_sequence(mixed):
    if isinstance(mixed, (dict, list, str)):
        raise TypeError(type(mixed).__name__)
    return iter(mixed)
