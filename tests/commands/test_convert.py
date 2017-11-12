import sys

import pytest

from bonobo.util.environ import change_working_directory
from bonobo.util.testing import all_runners


@pytest.mark.skipif(
    sys.version_info < (3, 6), reason="python 3.5 does not preserve kwargs order and this cant pass for now"
)
@all_runners
def test_convert(runner, tmpdir):
    csv_content = 'id;name\n1;Romain'
    tmpdir.join('in.csv').write(csv_content)

    with change_working_directory(tmpdir):
        runner('convert', 'in.csv', 'out.csv')

    assert tmpdir.join('out.csv').read().strip() == csv_content
