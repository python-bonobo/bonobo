Services and dependencies (draft implementation)
================================================

:Status: Draft implementation
:Stability: Alpha
:Last-Modified: 28 apr 2017

Most probably, you'll want to use external systems within your transformations. Those systems may include databases,
apis (using http, for example), filesystems, etc.

You can start by hardcoding those services. That does the job, at first.

If you're going a little further than that, you'll feel limited, for a few reasons:

* Hardcoded and tightly linked dependencies make your transformations hard to test, and hard to reuse.
* Processing data on your laptop is great, but being able to do it on different systems (or stages), in different
  environments, is more realistic? You probably want to contigure a different database on a staging environment,
  preprod environment or production system. Maybe you have silimar systems for different clients and want to select
  the system at runtime. Etc.

Service injection
:::::::::::::::::

To solve this problem, we introduce a light dependency injection system. It allows to define named dependencies in
your transformations, and provide an implementation at runtime.

Class-based transformations
---------------------------

To define a service dependency in a class-based transformation, use :class:`bonobo.config.Service`, a special
descriptor (and subclass of :class:`bonobo.config.Option`) that will hold the service names and act as a marker
for runtime resolution of service instances.

Let's define such a transformation:

.. code-block:: python

    from bonobo.config import Configurable, Service

    class JoinDatabaseCategories(Configurable):
        database = Service('primary_sql_database')

        def __call__(self, database, row):
            return {
                **row,
                'category': database.get_category_name_for_sku(row['sku'])
            }

This piece of code tells bonobo that your transformation expect a sercive called "primary_sql_database", that will be
injected to your calls under the parameter name "database".

Function-based transformations
------------------------------

No implementation yet, but expect something similar to CBT API, maybe using a `@Service(...)` decorator.

Execution
---------

Let's see how to execute it:

.. code-block:: python

    import bonobo

    graph = bonobo.graph(
        *before,
        JoinDatabaseCategories(),
        *after,
    )
    
    if __name__ == '__main__':
        bonobo.run(
            graph,
            services={
                'primary_sql_database': my_database_service,
            }
        )
    
A dictionary, or dictionary-like, "services" named argument can be passed to the :func:`bonobo.run` helper. The
"dictionary-like" part is the real keyword here. Bonobo is not a DIC library, and won't become one. So the implementation
provided is pretty basic, and feature-less. But you can use much more evolved libraries instead of the provided
stub, and as long as it works the same (a.k.a implements a dictionary-like interface), the system will use it.

Service configuration (to be decided and implemented)
:::::::::::::::::::::::::::::::::::::::::::::::::::::

* There should be a way to configure default service implementation for a python file, a directory, a project ...
* There should be a way to override services when running a transformation.
* There should be a way to use environment for service configuration.

Future and proposals
::::::::::::::::::::

This is the first proposed implementation and it will evolve, but looks a lot like how we used bonobo ancestor in
production.

May or may not happen, depending on discussions.

* Singleton or prototype based injection (to use spring terminology, see
  https://www.tutorialspoint.com/spring/spring_bean_scopes.htm), allowing smart factory usage and efficient sharing of
  resources.
* Lazily resolved parameters, eventually overriden by command line or environment, so you can for example override the
  database DSN or target filesystem on command line (or with shell environment).
* Pool based locks that ensure that only one (or n) transformations are using a given service at the same time.
* Simple config implementation, using a python file for config (ex: bonobo run ... --services=services_prod.py).
* Default configuration for services, using an optional callable (`def get_services(args): ...`). Maybe tie default
  configuration to graph, but not really a fan because this is unrelated to graph logic.
* Default implementation for a service in a transformation or in the descriptor. Maybe not a good idea, because it
  tends to push forward multiple instances of the same thing, but we maybe...
  
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


Read more
:::::::::

* See https://github.com/hartym/bonobo-sqlalchemy/blob/work-in-progress/bonobo_sqlalchemy/writers.py#L19 for example usage (work in progress).
