def force_iterator(x):
    if isinstance(x, str):
        return [x]
    try:
        return iter(x)
    except Exception as e:
        return [x] if x else []
