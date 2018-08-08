Part 4: Services
================

All external dependencies (like filesystems, network clients, database connections, etc.) should be provided to
transformations as a service. This will allow for great flexibility, including the ability to test your transformations isolated
from the external world and easily switch to production (being user-friendly for people in system administration).

In the last section, we used the `fs` service to access filesystems, we'll go even further by switching our `requests`
call to use the `http` service, so we can switch the `requests` session at runtime. We'll use it to add an http cache,
which is a great thing to avoid hammering a remote API.


Default services
::::::::::::::::

As a default, |bonobo| provides only two services:

* `fs`, a :obj:`fs.osfs.OSFS` object to access files.
* `http`, a :obj:`requests.Session` object to access the Web.


Overriding services
:::::::::::::::::::

You can override the default services, or define your own services, by providing a dictionary to the `services=`
argument of :obj:`bonobo.run`. First, let's rewrite get_services:

.. code-block:: python

    import requests

    def get_services():
        http = requests.Session()
        http.headers = {'User-Agent': 'Monkeys!'}
        return {
            'http': http
        }

Switching requests to use the service
:::::::::::::::::::::::::::::::::::::

Let's replace the :obj:`requests.get` call we used in the first steps to use the `http` service:

.. code-block:: python

    from bonobo.config import use

    @use('http')
    def extract_fablabs(http):
        yield from http.get(FABLABS_API_URL).json().get('records')

Tadaa, done! You're no more tied to a specific implementation, but to whatever :obj:`requests` -compatible object the
user wants to provide.

Adding cache
::::::::::::

Let's demonstrate the flexibility of this approach by adding some local cache for HTTP requests, to avoid hammering the
API endpoint as we run our tests.

First, let's install `requests-cache`:

.. code-block:: shell-session

    $ pip install requests-cache

Then, let's switch the implementation, conditionally.

.. code-block:: python

    def get_services(use_cache=False):
        if use_cache:
            from requests_cache import CachedSession
            http = CachedSession('http.cache')
        else:
            import requests
            http = requests.Session()

        return {
            'http': http
        }

Then in the main block, let's add support for a `--use-cache` argument:

.. code-block:: python

    if __name__ == '__main__':
        parser = bonobo.get_argument_parser()
        parser.add_argument('--use-cache', action='store_true', default=False)

        with bonobo.parse_args(parser) as options:
            bonobo.run(get_graph(**options), services=get_services(**options))

And you're done! Now, you can switch from using or not the cache using the `--use-cache` argument in command line when
running your job.


Moving forward
::::::::::::::

You now know:

* How to use builtin service implementations
* How to override a service
* How to define your own service
* How to tune the default argument parser

It's now time to jump to :doc:`5-packaging`.
