import os

import bonobo


def extract():
    my_secret = os.getenv('MY_SECRET')
    test_user_password = os.getenv('TEST_USER_PASSWORD')
    user = os.getenv('USERNAME')
    path = os.getenv('PATH')

    return my_secret, test_user_password, user, path


def load(s: str):
    print(s)


graph = bonobo.Graph(extract, load)

if __name__ == '__main__':
    bonobo.run(graph)
