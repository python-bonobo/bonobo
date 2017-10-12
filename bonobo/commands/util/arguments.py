import json


def parse_variable_argument(arg):
    try:
        key, val = arg.split('=', 1)
    except ValueError:
        return arg, True

    try:
        val = json.loads(val)
    except json.JSONDecodeError:
        pass

    return key, val


def test_parse_variable_argument():
    assert parse_variable_argument('foo=bar') == ('foo', 'bar')
    assert parse_variable_argument('foo="bar"') == ('foo', 'bar')
    assert parse_variable_argument('sep=";"') == ('sep', ';')
    assert parse_variable_argument('foo') == ('foo', True)


if __name__ == '__main__':
    test_parse_var()
