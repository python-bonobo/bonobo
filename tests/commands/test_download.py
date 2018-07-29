import io
from unittest.mock import patch

import pytest

from bonobo.commands.download import EXAMPLES_BASE_URL
from bonobo.util.testing import all_runners


@all_runners
def test_download_works_for_examples(runner):
    expected_bytes = b"hello world"

    class MockResponse(object):
        def __init__(self):
            self.status_code = 200

        def iter_content(self, *args, **kwargs):
            return [expected_bytes]

        def __enter__(self):
            return self

        def __exit__(self, *args, **kwargs):
            pass

    fout = io.BytesIO()
    fout.close = lambda: None

    with patch("bonobo.commands.download._open_url") as mock_open_url, patch(
        "bonobo.commands.download.open"
    ) as mock_open:
        mock_open_url.return_value = MockResponse()
        mock_open.return_value = fout
        runner("download", "examples/datasets/coffeeshops.txt")
    expected_url = EXAMPLES_BASE_URL + "datasets/coffeeshops.txt"
    mock_open_url.assert_called_once_with(expected_url)

    assert fout.getvalue() == expected_bytes


@all_runners
def test_download_fails_non_example(runner):
    with pytest.raises(ValueError):
        runner("download", "something/entirely/different.txt")
