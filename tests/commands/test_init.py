import os

from bonobo.util.testing import all_runners


@all_runners
def test_init_file(runner, tmpdir):
    target = tmpdir.join('foo.py')
    target_filename = str(target)
    runner('init', target_filename)
    assert os.path.exists(target_filename)

    out, err = runner('run', target_filename)
    assert out.replace('\n', ' ').strip() == 'Hello World'
    assert not err