"""
Execution Contexts are objects that wraps the stateless data-structures (graphs and nodes) during a job execution to
keep an eye on their context/state (from the simplest things like i/o statistics to lifecycle and custom userland
state).

"""

from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.execution.contexts.plugin import PluginExecutionContext

__all__ = ['GraphExecutionContext', 'NodeExecutionContext', 'PluginExecutionContext']
