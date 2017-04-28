import pytest

from bonobo import Bag, FileReader, FileWriter, open_fs
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext


@pytest.mark.parametrize(
    'lines,output',
    [
        (('ACME', ), 'ACME'),  # one line...
        (('Foo', 'Bar', 'Baz'), 'Foo\nBar\nBaz'),  # more than one line...
    ]
)
def test_file_writer_in_context(tmpdir, lines, output):
    fs, filename = open_fs(tmpdir), 'output.txt'

    writer = FileWriter(path=filename)
    context = NodeExecutionContext(writer, services={'fs': fs})

    context.start()
    context.recv(BEGIN, *map(Bag, lines), END)
    for i in range(len(lines)):
        context.step()
    context.stop()

    assert fs.open(filename).read() == output


def test_file_writer_out_of_context(tmpdir):
    fs, filename = open_fs(tmpdir), 'output.txt'

    writer = FileWriter(path=filename)

    with writer.open(fs) as fp:
        fp.write('Yosh!')

    assert fs.open(filename).read() == 'Yosh!'


def test_file_reader_in_context(tmpdir):
    fs, filename = open_fs(tmpdir), 'input.txt'

    fs.open(filename, 'w').write('Hello\nWorld\n')

    reader = FileReader(path=filename)
    context = CapturingNodeExecutionContext(reader, services={'fs': fs})

    context.start()
    context.recv(BEGIN, Bag(), END)
    context.step()
    context.stop()

    assert len(context.send.mock_calls) == 2

    args0, kwargs0 = context.send.call_args_list[0]
    assert len(args0) == 1 and not len(kwargs0)
    args1, kwargs1 = context.send.call_args_list[1]
    assert len(args1) == 1 and not len(kwargs1)

    assert args0[0].args[0] == 'Hello'
    assert args1[0].args[0] == 'World'
