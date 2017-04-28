from bonobo import get_examples_path, open_fs


def get_services():
    return {'fs': open_fs(get_examples_path())}
