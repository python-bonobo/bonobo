from bonobo.strategies.executor import ProcessPoolExecutorStrategy, ThreadPoolExecutorStrategy
from bonobo.strategies.naive import NaiveStrategy

__all__ = [
    'create_strategy',
]

STRATEGIES = {
    'naive': NaiveStrategy,
    'processpool': ProcessPoolExecutorStrategy,
    'threadpool': ThreadPoolExecutorStrategy,
}

DEFAULT_STRATEGY = 'threadpool'


def create_strategy(name=None):
    """
    Create a strategy, or just returns it if it's already one.
    
    :param name: 
    :return: Strategy
    """
    from bonobo.strategies.base import Strategy
    import logging

    if isinstance(name, Strategy):
        return name

    if name is None:
        name = DEFAULT_STRATEGY

    logging.debug('Creating strategy {}...'.format(name))

    try:
        factory = STRATEGIES[name]
    except KeyError as exc:
        raise RuntimeError(
            'Invalid strategy {}. Available choices: {}.'.format(repr(name), ', '.join(sorted(STRATEGIES.keys())))
        ) from exc

    return factory()