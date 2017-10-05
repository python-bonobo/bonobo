Settings & Environment
======================

.. module:: bonobo.settings

All settings that you can find in the :mod:`bonobo.settings` module. You can override those settings using
environment variables. For you own settings and configuration values, see the :doc:`/guide/environment` guide.

Debug
:::::

:Purpose: Sets the debug mode, which is more verbose. Loglevel will be lowered to DEBUG instead of INFO.
:Environment: `DEBUG`
:Setting: `bonobo.settings.DEBUG`
:Default: `False`

Profile
:::::::

:Purpose: Sets profiling, which adds memory/cpu usage output. Not yet fully implemented. It is expected that setting
          this to true will have a non-neglictible performance impact.
:Environment: `PROFILE`
:Setting: `bonobo.settings.PROFILE`
:Default: `False`

Quiet
:::::

:Purpose: Sets the quiet mode, which ask any output to be computer parsable. Formating will be removed, but it will
          allow to use unix pipes, etc. Not yet fully implemented, few transformations already use it. Probably, it
          should be the default on non-interactive terminals.
:Environment: `QUIET`
:Setting: `bonobo.settings.QUIET`
:Default: `False`

Logging Level
:::::::::::::

:Purpose: Sets the python minimum logging level.
:Environment: `LOGGING_LEVEL`
:Setting: `bonobo.settings.LOGGING_LEVEL`
:Default: `DEBUG` if DEBUG is False, otherwise `INFO`
:Values: `CRITICAL`, `FATAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET`

I/O Format
::::::::::

:Purpose: Sets default input/output format for builtin transformations. It can be overriden on each node. The `kwargs`
          value means that each node will try to read its input from keywords arguments (and write similar formated
          output), while `arg0` means it will try to read its input from the first positional argument (and write
          similar formated output).
:Environment: `IOFORMAT`
:Setting: `bonobo.settings.IOFORMAT`
:Default: `kwargs`
:Values: `kwargs`, `arg0`


