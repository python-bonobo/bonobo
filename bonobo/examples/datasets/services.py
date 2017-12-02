import bonobo


def get_services():
    return {
        'fs': bonobo.open_fs(bonobo.get_examples_path('datasets'))
    }