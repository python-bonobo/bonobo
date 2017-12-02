import os

import bonobo


def get_datasets_dir(*dirs):
    home_dir = os.path.expanduser('~')
    target_dir = os.path.join(
        home_dir, '.cache/bonobo', bonobo.__version__, *dirs
    )
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def get_services():
    return {'fs': bonobo.open_fs(get_datasets_dir('datasets'))}
