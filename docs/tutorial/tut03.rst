Configurables and Services
==========================

.. note::

    This section lacks completeness, sorry for that (but you can still read it!).

In the last section, we used a few new tools.

Class-based transformations and configurables
:::::::::::::::::::::::::::::::::::::::::::::

Bonobo is a bit dumb. If something is callable, it considers it can be used as a transformation, and it's up to the
user to provide callables that logically fits in a graph.

You can use plain python objects with a `__call__()` method, and it will just work.

As a lot of transformations needs common machinery, there is a few tools to quickly build transformations, most of
them requiring your class to subclass :class:`bonobo.config.Configurable`.

Configurables allows to use the following features:

* You can add **Options** (using the :class:`bonobo.config.Option` descriptor). Options can be positional, or keyword
  based, can have a default value and will be consumed from the constructor arguments.

    .. code-block:: python

        from bonobo.config import Configurable, Option

        class PrefixIt(Configurable):
            prefix = Option(str, positional=True, default='>>>')

            def call(self, row):
                return self.prefix + ' ' + row

        prefixer = PrefixIt('$')

* You can add **Services** (using the :class:`bonobo.config.Service` descriptor). Services are a subclass of
  :class:`bonobo.config.Option`, sharing the same basics, but specialized in the definition of "named services" that
  will be resolved at runtime (a.k.a for which we will provide an implementation at runtime). We'll dive more into that
  in the next section

    .. code-block:: python

        from bonobo.config import Configurable, Option, Service

        class HttpGet(Configurable):
            url = Option(default='https://jsonplaceholder.typicode.com/users')
            http = Service('http.client')

            def call(self, http):
                resp = http.get(self.url)

                for row in resp.json():
                    yield row

        http_get = HttpGet()


* You can add **Methods** (using the :class:`bonobo.config.Method` descriptor). :class:`bonobo.config.Method` is a
  subclass of :class:`bonobo.config.Option` that allows to pass callable parameters, either to the class constructor,
  or using the class as a decorator.

    .. code-block:: python

        from bonobo.config import Configurable, Method

        class Applier(Configurable):
            apply = Method()

            def call(self, row):
                return self.apply(row)

        @Applier
        def Prefixer(self, row):
            return 'Hello, ' + row

        prefixer = Prefixer()

* You can add **ContextProcessors**, which are an advanced feature we won't introduce here. If you're familiar with
  pytest, you can think of them as pytest fixtures, execution wise.

Services
::::::::

The motivation behind services is mostly separation of concerns, testability and deployability.

Usually, your transformations will depend on services (like a filesystem, an http client, a database, a rest api, ...).
Those services can very well be hardcoded in the transformations, but there is two main drawbacks:

* You won't be able to change the implementation depending on the current environment (development laptop versus
  production servers, bug-hunting session versus execution, etc.)
* You won't be able to test your transformations without testing the associated services.

To overcome those caveats of hardcoding things, we define Services in the configurable, which are basically
string-options of the service names, and we provide an implementation at the last moment possible.

There are two ways of providing implementations:

* Either file-wide, by providing a `get_services()` function that returns a dict of named implementations (we did so
  with filesystems in the previous step, :doc:`tut02`)
* Either directory-wide, by providing a `get_services()` function in a specially named `_services.py` file.

The first is simpler if you only have one transformation graph in one file, the second allows to group coherent
transformations together in a directory and share the implementations.

Let's see how to use it, starting from the previous service example:

.. code-block:: python

    from bonobo.config import Configurable, Option, Service

    class HttpGet(Configurable):
        url = Option(default='https://jsonplaceholder.typicode.com/users')
        http = Service('http.client')

        def call(self, http):
            resp = http.get(self.url)

            for row in resp.json():
                yield row

We defined an "http.client" service, that obviously should have a `get()` method, returning responses that have a
`json()` method.

Let's provide two implementations for that. The first one will be using `requests <http://docs.python-requests.org/>`_,
that coincidally satisfies the described interface:

.. code-block:: python

    import bonobo
    import requests

    def get_services():
        return {
            'http.client': requests
        }

    graph = bonobo.Graph(
        HttpGet(),
        print,
    )

If you run this code, you should see some mock data returned by the webservice we called (assuming it's up and you can
reach it).

Now, the second implementation will replace that with a mock, used for testing purposes:

.. code-block:: python

    class HttpResponseStub:
        def json(self):
            return [
                {'id': 1, 'name': 'Leanne Graham', 'username': 'Bret', 'email': 'Sincere@april.biz', 'address': {'street': 'Kulas Light', 'suite': 'Apt. 556', 'city': 'Gwenborough', 'zipcode': '92998-3874', 'geo': {'lat': '-37.3159', 'lng': '81.1496'}}, 'phone': '1-770-736-8031 x56442', 'website': 'hildegard.org', 'company': {'name': 'Romaguera-Crona', 'catchPhrase': 'Multi-layered client-server neural-net', 'bs': 'harness real-time e-markets'}},
                {'id': 2, 'name': 'Ervin Howell', 'username': 'Antonette', 'email': 'Shanna@melissa.tv', 'address': {'street': 'Victor Plains', 'suite': 'Suite 879', 'city': 'Wisokyburgh', 'zipcode': '90566-7771', 'geo': {'lat': '-43.9509', 'lng': '-34.4618'}}, 'phone': '010-692-6593 x09125', 'website': 'anastasia.net', 'company': {'name': 'Deckow-Crist', 'catchPhrase': 'Proactive didactic contingency', 'bs': 'synergize scalable supply-chains'}},
            ]

    class HttpStub:
        def get(self, url):
            return HttpResponseStub()

    def get_services():
        return {
            'http.client': HttpStub()
        }

    graph = bonobo.Graph(
        HttpGet(),
        print,
    )

The `Graph` definition staying the exact same, you can easily substitute the `_services.py` file depending on your
environment (the way you're doing this is out of bonobo scope and heavily depends on your usual way of managing
configuration files on different platforms).

Starting with bonobo 0.5 (not yet released), you will be able to use service injections with function-based
transformations too, using the `bonobo.config.requires` decorator to mark a dependency.

.. code-block:: python

    from bonobo.config import requires

    @requires('http.client')
    def http_get(http):
        resp = http.get('https://jsonplaceholder.typicode.com/users')

        for row in resp.json():
            yield row


Read more
:::::::::

* :doc:`/guide/services`
* :doc:`/reference/api_config`

Next
::::

:doc:`tut04`.
