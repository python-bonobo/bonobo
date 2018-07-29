import pytest

from bonobo import FileReader, FileWriter
from bonobo.constants import EMPTY
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.util.testing import BufferingNodeExecutionContext, FilesystemTester

txt_tester = FilesystemTester("txt")
txt_tester.input_data = "Hello\nWorld\n"


def test_file_writer_contextless(tmpdir):
    fs, filename, services = txt_tester.get_services_for_writer(tmpdir)

    with FileWriter(path=filename).open(fs) as fp:
        fp.write("Yosh!")

    with fs.open(filename) as fp:
        assert fp.read() == "Yosh!"


@pytest.mark.parametrize(
    "lines,output",
    [(("ACME",), "ACME"), (("Foo", "Bar", "Baz"), "Foo\nBar\nBaz")],  # one line...  # more than one line...
)
def test_file_writer_in_context(tmpdir, lines, output):
    fs, filename, services = txt_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(FileWriter(path=filename), services=services) as context:
        context.write_sync(*lines)

    with fs.open(filename) as fp:
        assert fp.read() == output


def test_file_reader(tmpdir):
    fs, filename, services = txt_tester.get_services_for_reader(tmpdir)

    with BufferingNodeExecutionContext(FileReader(path=filename), services=services) as context:
        context.write_sync(EMPTY)

    output = context.get_buffer()
    assert len(output) == 2
    assert output[0] == ("Hello",)
    assert output[1] == ("World",)
