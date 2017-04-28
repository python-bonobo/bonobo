from os.path import dirname

import bonobo


def get_services():
    return {'fs': bonobo.open_fs(dirname(__file__))}
