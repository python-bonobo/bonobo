import pytest

from bonobo import Bag, FileReader, FileWriter
from bonobo.constants import BEGIN, END
from bonobo.execution import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext


@pytest.mark.parametrize(
    'lines,output',
    [
        (('ACME',), 'ACME'),  # one line...
        (('Foo', 'Bar', 'Baz'), 'Foo\nBar\nBaz'),  # more than one line...
    ]
)
def test_file_writer_in_context(tmpdir, lines, output):
    file = tmpdir.join('output.txt')

    writer = FileWriter(path=str(file))
    context = NodeExecutionContext(writer, None)

    context.start()
    context.recv(BEGIN, *map(Bag, lines), END)
    for i in range(len(lines)):
        context.step()
    context.stop()

    assert file.read() == output


def test_file_writer_out_of_context(tmpdir):
    file = tmpdir.join('output.txt')
    writer = FileWriter(path=str(file))

    with writer.open() as fp:
        fp.write('Yosh!')

    assert file.read() == 'Yosh!'


def test_file_reader_in_context(tmpdir):
    file = tmpdir.join('input.txt')
    file.write('Hello\nWorld\n')

    reader = FileReader(path=str(file))
    context = CapturingNodeExecutionContext(reader, None)

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
