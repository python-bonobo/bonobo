def set_meta(**kwargs):
    def setter(obj):
        obj.__meta__ = get_all_meta(obj)
        obj.__meta__.update(kwargs)
        return obj

    return setter


_unspecified = object()


def get_meta(obj, name, default=_unspecified):
    try:
        return get_all_meta(obj)[name]
    except KeyError as exc:
        if default is not _unspecified:
            return default
        raise


def get_all_meta(obj):
    try:
        return obj.__meta__
    except AttributeError:
        try:
            obj.__meta__ = dict()
        except AttributeError:
            return {}
        return obj.__meta__
