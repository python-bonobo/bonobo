from bonobo import inject, service


class MyFoo():
    pass


def test_service_is_singleton():
    @service
    def foo():
        return MyFoo()

    assert foo() is foo()

    @inject(foo)
    def bar(myfoo):
        assert myfoo is foo()

    bar()

    foo2 = foo.define()

    assert type(foo()) == type(foo2())
    assert foo2() is not foo()
