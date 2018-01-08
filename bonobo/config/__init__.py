from bonobo.config.configurables import Configurable
from bonobo.config.functools import transformation_factory
from bonobo.config.options import Method, Option
from bonobo.config.processors import ContextProcessor, use_context, use_context_processor, use_raw_input, use_no_input
from bonobo.config.services import Container, Exclusive, Service, use, create_container
from bonobo.util import deprecated_alias

requires = deprecated_alias('requires', use)

# Bonobo's Config API
__all__ = [
    'Configurable',
    'Container',
    'ContextProcessor',
    'Exclusive',
    'Method',
    'Option',
    'Service',
    'create_container',
    'requires',
    'transformation_factory',
    'use',
    'use_context',
    'use_context_processor',
    'use_no_input',
    'use_raw_input',
]
