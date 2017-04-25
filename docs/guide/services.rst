Services and dependencies (draft implementation)
================================================

Most probably, you'll want to use external systems within your transformations. Those systems may include databases,
apis (using http, for example), filesystems, etc.

For a start, including those services hardcoded in your transformations can do the job, but you'll pretty soon feel
limited, for two main reasons:

* Hardcoded and tightly linked dependencies make your transformation atoms hard to test.
* Processing data on your laptop is great, but being able to do it on different systems (or stages), in different
  environments, is more realistic.

Service injection
:::::::::::::::::

To solve this problem, we introduce a light dependency injection system that basically allows you to define named
dependencies in your transformations, and provide an implementation at runtime.

Let's define such a transformation:

.. code-block:: python

    from bonobo.config import Configurable, Service

    class JoinDatabaseCategories(Configurable):
        database = Service(default='primary_sql_database')

        def __call__(self, database, row):
            return {
                **row,
                'category': database.get_category_name_for_sku(row['sku'])
            }

This piece of code tells bonobo that your transformation expect a sercive called "primary_sql_database", that will be
injected to your calls under the parameter name "database".

Let's see how to execute it:

.. code-block:: python

    import bonobo

    bonobo.run(
        [...extract...],
        JoinDatabaseCategories(),
        [...load...],
        services={
            'primary_sql_database': my_database_service,
        }
    )

Future
::::::

This is the first proposed implementation and it will evolve, but looks a lot like how we used bonobo ancestor in
production.

You can expect to see the following features pretty soon:

* Singleton or prototype based injection (to use spring terminology, see
  https://www.tutorialspoint.com/spring/spring_bean_scopes.htm), allowing smart factory usage and efficient sharing of
  resources.
* Lazily resolved parameters, eventually overriden by command line or environment, so you can for example override the
  database DSN or target filesystem on command line (or with shell environment).
* Pool based locks that ensure that only one (or n) transformations are using a given service at the same time.

This is under heavy development, let us know what you think (slack may be a good place for this).


Read more
:::::::::

todo: example code.
