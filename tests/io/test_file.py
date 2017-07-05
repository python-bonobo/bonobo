import pytest

from bonobo import Bag, FileReader, FileWriter
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext, FilesystemTester

txt_tester = FilesystemTester('txt')
txt_tester.input_data = 'Hello\nWorld\n'


def test_file_writer_contextless(tmpdir):
    fs, filename, services = txt_tester.get_services_for_writer(tmpdir)

    with FileWriter(path=filename).open(fs) as fp:
        fp.write('Yosh!')

    with fs.open(filename) as fp:
        assert fp.read() == 'Yosh!'


@pytest.mark.parametrize(
    'lines,output',
    [
        (('ACME', ), 'ACME'),  # one line...
        (('Foo', 'Bar', 'Baz'), 'Foo\nBar\nBaz'),  # more than one line...
    ]
)
def test_file_writer_in_context(tmpdir, lines, output):
    fs, filename, services = txt_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(FileWriter(path=filename), services=services) as context:
        context.write(BEGIN, *map(Bag, lines), END)
        for _ in range(len(lines)):
            context.step()

    with fs.open(filename) as fp:
        assert fp.read() == output


def test_file_reader(tmpdir):
    fs, filename, services = txt_tester.get_services_for_reader(tmpdir)

    with CapturingNodeExecutionContext(FileReader(path=filename), services=services) as context:
        context.write(BEGIN, Bag(), END)
        context.step()

    assert len(context.send.mock_calls) == 2

    args0, kwargs0 = context.send.call_args_list[0]
    assert len(args0) == 1 and not len(kwargs0)
    args1, kwargs1 = context.send.call_args_list[1]
    assert len(args1) == 1 and not len(kwargs1)

    assert args0[0].args[0] == 'Hello'
    assert args1[0].args[0] == 'World'
