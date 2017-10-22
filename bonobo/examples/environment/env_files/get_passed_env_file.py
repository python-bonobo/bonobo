import os

import bonobo


def extract():
    my_secret = os.getenv('MY_SECRET')
    test_user_password = os.getenv('TEST_USER_PASSWORD')
    path = os.getenv('PATH')

    yield my_secret
    yield test_user_password
    yield path


def load(s: str):
    print(s)


graph = bonobo.Graph(extract, load)

if __name__ == '__main__':
    bonobo.run(graph)
