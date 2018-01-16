Services
========

.. warning::

   This is a "future" document, that does not exist, it's only kept here not to lose the data until we organize better
   documentation versioning.

Future and proposals
::::::::::::::::::::

This is a first implementation and it will evolve. Base concepts will stay the same though.

May or may not happen, depending on discussions.

* Singleton or prototype based injection (to use spring terminology, see
  https://www.tutorialspoint.com/spring/spring_bean_scopes.htm), allowing smart factory usage and efficient sharing of
  resources.
* Lazily resolved parameters, eventually overriden by command line or environment, so you can for example override the
  database DSN or target filesystem on command line (or with shell environment vars).
* Pool based locks that ensure that only one (or n) transformations are using a given service at the same time.
* Simple config implementation, using a python file for config (ex: bonobo run ... --services=services_prod.py).
* Default configuration for services, using an optional callable (`def get_services(args): ...`). Maybe tie default
  configuration to graph, but not really a fan because this is unrelated to graph logic.
* Default implementation for a service in a transformation or in the descriptor. Maybe not a good idea, because it
  tends to push forward multiple instances of the same thing, but maybe...

  A few ideas on how it can be implemented, from the user perspective.

  .. code-block:: python

      # using call
      http = Service('http.client')(requests)

      # using more explicit call
      http = Service('http.client').set_default_impl(requests)

      # using a decorator
      @Service('http.client')
      def http(self, services):
          import requests
          return requests

      # as a default in a subclass of Service
      class HttpService(Service):
          def get_default_impl(self, services):
              import requests
              return requests

      # ... then use it as another service
      http = HttpService('http.client')


This is under development, let us know what you think (slack may be a good place for this).
The basics already work, and you can try it.

