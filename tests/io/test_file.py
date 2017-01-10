import pytest

from bonobo import FileWriter, Bag, FileReader
from bonobo.core.contexts import ComponentExecutionContext
from bonobo.util.testing import CapturingComponentExecutionContext
from bonobo.util.tokens import BEGIN, END


@pytest.mark.parametrize(
    'lines,output',
    [
        (('ACME', ), 'ACME'),  # one line...
        (('Foo', 'Bar', 'Baz'), 'Foo\nBar\nBaz'),  # more than one line...
    ]
)
def test_file_writer_in_context(tmpdir, lines, output):
    file = tmpdir.join('output.txt')

    writer = FileWriter(str(file))
    context = ComponentExecutionContext(writer, None)

    context.initialize()
    context.recv(BEGIN, *map(Bag, lines), END)
    for i in range(len(lines)):
        context.step()
    context.finalize()

    assert file.read() == output

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_file_writer_out_of_context(tmpdir):
    file = tmpdir.join('output.txt')
    writer = FileWriter(str(file))
    fp = writer.open()
    fp.write('Yosh!')
    writer.close(fp)

    assert file.read() == 'Yosh!'


def test_file_reader_in_context(tmpdir):
    file = tmpdir.join('input.txt')
    file.write('Hello\nWorld\n')

    reader = FileReader(str(file))
    context = CapturingComponentExecutionContext(reader, None)

    context.initialize()
    context.recv(BEGIN, Bag(), END)
    context.step()
    context.finalize()

    assert len(context.send.mock_calls) == 2

    args0, kwargs0 = context.send.call_args_list[0]
    assert len(args0) == 1 and not len(kwargs0)
    args1, kwargs1 = context.send.call_args_list[1]
    assert len(args1) == 1 and not len(kwargs1)

    assert args0[0].args[0] == 'Hello'
    assert args1[0].args[0] == 'World'
