import pytest

from bonobo.config.configurables import Configurable
from bonobo.config.options import Option
from bonobo.config.services import Container, Service, validate_service_name


class MyConfigurable(Configurable):
    required_str = Option(str, required=True)
    default_str = Option(str, default='foo')
    integer = Option(int)


class MyHarderConfigurable(MyConfigurable):
    also_required = Option(bool, required=True)


class MyBetterConfigurable(MyConfigurable):
    required_str = Option(str, required=False, default='kaboom')


class PrinterInterface():
    def print(self, *args):
        raise NotImplementedError()


class ConcretePrinter(PrinterInterface):
    def __init__(self, prefix):
        self.prefix = prefix

    def print(self, *args):
        return ';'.join((self.prefix, *args))


class MyServiceDependantConfigurable(Configurable):
    printer = Service(PrinterInterface, )

    def __call__(self, printer: PrinterInterface, *args):
        return printer.print(*args)


def test_missing_required_option_error():
    with pytest.raises(TypeError) as exc:
        MyConfigurable()
    assert exc.match('missing 1 required option:')


def test_missing_required_options_error():
    with pytest.raises(TypeError) as exc:
        MyHarderConfigurable()
    assert exc.match('missing 2 required options:')


def test_extraneous_option_error():
    with pytest.raises(TypeError) as exc:
        MyConfigurable(required_str='foo', hello='world')
    assert exc.match('got 1 unexpected option:')


def test_extraneous_options_error():
    with pytest.raises(TypeError) as exc:
        MyConfigurable(required_str='foo', hello='world', acme='corp')
    assert exc.match('got 2 unexpected options:')


def test_defaults():
    o = MyConfigurable(required_str='hello')
    assert o.required_str == 'hello'
    assert o.default_str == 'foo'
    assert o.integer == None


def test_str_type_factory():
    o = MyConfigurable(required_str=42)
    assert o.required_str == '42'
    assert o.default_str == 'foo'
    assert o.integer == None


def test_int_type_factory():
    o = MyConfigurable(required_str='yo', default_str='bar', integer='42')
    assert o.required_str == 'yo'
    assert o.default_str == 'bar'
    assert o.integer == 42


def test_bool_type_factory():
    o = MyHarderConfigurable(required_str='yes', also_required='True')
    assert o.required_str == 'yes'
    assert o.default_str == 'foo'
    assert o.integer == None
    assert o.also_required == True


def test_option_resolution_order():
    o = MyBetterConfigurable()
    assert o.required_str == 'kaboom'
    assert o.default_str == 'foo'
    assert o.integer == None


def test_service_name_validator():
    assert validate_service_name('foo') == 'foo'
    assert validate_service_name('foo.bar') == 'foo.bar'
    assert validate_service_name('Foo') == 'Foo'
    assert validate_service_name('Foo.Bar') == 'Foo.Bar'
    assert validate_service_name('Foo.a0') == 'Foo.a0'

    with pytest.raises(ValueError):
        validate_service_name('foo.0')

    with pytest.raises(ValueError):
        validate_service_name('0.foo')


SERVICES = Container(
    printer0=ConcretePrinter(prefix='0'),
    printer1=ConcretePrinter(prefix='1'),
)


def test_service_dependency():
    o = MyServiceDependantConfigurable(printer='printer0')

    assert o(SERVICES.get('printer0'), 'foo', 'bar') == '0;foo;bar'
    assert o(SERVICES.get('printer1'), 'bar', 'baz') == '1;bar;baz'
    assert o(*SERVICES.args_for(o), 'foo', 'bar') == '0;foo;bar'


def test_service_dependency_unavailable():
    o = MyServiceDependantConfigurable(printer='printer2')
    with pytest.raises(KeyError):
        SERVICES.args_for(o)
