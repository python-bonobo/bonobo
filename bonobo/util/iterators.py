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
