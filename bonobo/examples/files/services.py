from bonobo import examples, open_fs


def get_services():
    return {**examples.get_services(), "fs.output": open_fs()}
