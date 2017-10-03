import os

from bonobo import Graph


def extract():
    env_test_user = os.getenv('ENV_TEST_USER')
    env_test_number = os.getenv('ENV_TEST_NUMBER')
    env_test_string = os.getenv('ENV_TEST_STRING')
    return env_test_user, env_test_number, env_test_string


def load(s: str):
    print(s)


graph = Graph(extract, load)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
