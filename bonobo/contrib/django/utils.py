def create_or_update(model, *, defaults=None, save=True, **kwargs):
    """
    Create or update a django model instance.

    :param model:
    :param defaults:
    :param kwargs:
    :return: object, created, updated

    """
    obj, created = model._default_manager.get_or_create(defaults=defaults, **kwargs)

    updated = False
    if not created:
        if defaults:
            for k, v in defaults.items():
                if getattr(obj, k) != v:
                    setattr(obj, k, v)
                    updated = True

        if updated and save:
            obj.save()

    return obj, created, updated
