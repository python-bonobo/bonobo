from mock import patch

from bonobo.ext.opendatasoft import from_opendatasoft_api


class ResponseMock:
    def __init__(self, json_value):
        self.json_value = json_value
        self.count = 0

    def json(self):
        if self.count:
            return {}
        else:
            self.count += 1
            return {'records': self.json_value, }


def test_read_from_opendatasoft_api():
    extract = from_opendatasoft_api('http://example.com/', 'test-a-set')
    with patch(
            'requests.get', return_value=ResponseMock([
                {
                    'fields': {
                        'foo': 'bar'
                    }
                },
                {
                    'fields': {
                        'foo': 'zab'
                    }
                },
            ])):
        for line in extract():
            assert 'foo' in line
