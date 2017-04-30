from bonobo import open_examples_fs


def get_services():
    return {'fs': open_examples_fs('datasets')}
