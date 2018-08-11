import os

import bonobo


def get_minor_version():
    return '.'.join(bonobo.__version__.split('.')[:2])


def get_datasets_dir(*dirs):
    home_dir = os.path.expanduser('~')
    target_dir = os.path.join(home_dir, '.cache/bonobo', get_minor_version(), *dirs)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def get_services():
    return {'fs': bonobo.open_fs(get_datasets_dir('datasets'))}
