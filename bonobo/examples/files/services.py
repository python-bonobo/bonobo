from bonobo import open_fs, examples


def get_services():
    return {
        **examples.get_services(),
        'fs.output': open_fs(),
    }
