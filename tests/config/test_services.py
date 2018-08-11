import threading
import time

import pytest

from bonobo.config import Configurable, Container, Exclusive, Service, use
from bonobo.config.services import create_container, validate_service_name
from bonobo.util import get_name


class PrinterInterface:
    def print(self, *args):
        raise NotImplementedError()


class ConcretePrinter(PrinterInterface):
    def __init__(self, prefix):
        self.prefix = prefix

    def print(self, *args):
        return ";".join((self.prefix, *args))


SERVICES = Container(printer0=ConcretePrinter(prefix="0"), printer1=ConcretePrinter(prefix="1"))


class MyServiceDependantConfigurable(Configurable):
    printer = Service(PrinterInterface)

    def __call__(self, *args, printer: PrinterInterface):
        return printer.print(*args)


def test_service_name_validator():
    assert validate_service_name("foo") == "foo"
    assert validate_service_name("foo.bar") == "foo.bar"
    assert validate_service_name("Foo") == "Foo"
    assert validate_service_name("Foo.Bar") == "Foo.Bar"
    assert validate_service_name("Foo.a0") == "Foo.a0"

    with pytest.raises(ValueError):
        validate_service_name("foo.0")

    with pytest.raises(ValueError):
        validate_service_name("0.foo")


def test_service_dependency():
    o = MyServiceDependantConfigurable(printer="printer0")

    assert o("foo", "bar", printer=SERVICES.get("printer0")) == "0;foo;bar"
    assert o("bar", "baz", printer=SERVICES.get("printer1")) == "1;bar;baz"
    assert o("foo", "bar", **SERVICES.kwargs_for(o)) == "0;foo;bar"


def test_service_dependency_unavailable():
    o = MyServiceDependantConfigurable(printer="printer2")
    with pytest.raises(KeyError):
        SERVICES.kwargs_for(o)


class VCR:
    def __init__(self):
        self.tape = []

    def append(self, x):
        return self.tape.append(x)


def test_exclusive():
    vcr = VCR()
    vcr.append("hello")

    def record(prefix, vcr=vcr):
        with Exclusive(vcr):
            for i in range(5):
                vcr.append(" ".join((prefix, str(i))))
                time.sleep(0.05)

    threads = [threading.Thread(target=record, args=(str(i),)) for i in range(5)]

    for thread in threads:
        thread.start()
        time.sleep(0.01)  # this is not good practice, how to test this without sleeping ?? XXX

    for thread in threads:
        thread.join()

    assert vcr.tape == [
        "hello",
        "0 0",
        "0 1",
        "0 2",
        "0 3",
        "0 4",
        "1 0",
        "1 1",
        "1 2",
        "1 3",
        "1 4",
        "2 0",
        "2 1",
        "2 2",
        "2 3",
        "2 4",
        "3 0",
        "3 1",
        "3 2",
        "3 3",
        "3 4",
        "4 0",
        "4 1",
        "4 2",
        "4 3",
        "4 4",
    ]


def test_requires():
    vcr = VCR()

    services = Container(output=vcr.append)

    @use("output")
    def append(out, x):
        out(x)

    svcargs = services.kwargs_for(append)
    assert len(svcargs) == 1
    assert svcargs["output"] == vcr.append


def test_constructor():
    c1 = Container(foo="foo", bar="bar")
    assert 2 == len(c1)

    c2 = Container({"foo": "foo", "bar": "bar"})
    assert 2 == len(c2)

    assert c1["foo"] == c2["foo"]
    assert c1["bar"] == c2["bar"]

    with pytest.raises(ValueError):
        Container({"bar": "bar"}, foo="foo")


@pytest.mark.parametrize("services", [None, {}])
def test_create_container_empty_values(services):
    c = create_container(services)
    assert len(c) == 2
    assert "fs" in c and get_name(c["fs"]) == "OSFS"
    assert "http" in c and get_name(c["http"]) == "requests"


def test_create_container_override():
    c = create_container({"http": "http", "fs": "fs"})
    assert len(c) == 2
    assert "fs" in c and c["fs"] == "fs"
    assert "http" in c and c["http"] == "http"
