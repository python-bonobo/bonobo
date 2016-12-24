from bonobo import inject

try:
    import couchdb
except ImportError as e:
    import logging

    logging.exception('You must install couchdb to use the bonobo couchdb extension. Easiest way is to install the '
                      'optional "couchdb" dependencies with «pip install bonobo[couchdb]», but you can also install a '
                      'specific version by yourself.')

import datetime

from bonobo import service


@service
def client(username, password):
    client = couchdb.Server()
    client.resource.credentials = (
        username,
        password, )
    return client


@service
@inject(client)
def database(client, name):
    return client[name]


def json_datetime(dt=None):
    dt = dt or datetime.datetime.now()
    return dt.replace(microsecond=0).isoformat() + 'Z'


@inject(database)
def query(db, map, reduce, *args, **kwargs):
    pass


cli1 = client.define('admin', 'admin')
cli2 = client.define('foo', 'bar')


@inject(client[cli1])
def print_db(db):
    print(db)


@inject(client[cli2])
def print_db2(db):
    print(db)


if __name__ == '__main__':
    print_db()
    print_db2()
    print_db()
    print_db2()
