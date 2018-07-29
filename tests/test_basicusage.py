from unittest.mock import patch

import pytest

import bonobo
from bonobo.execution.contexts.graph import GraphExecutionContext


@pytest.mark.timeout(2)
def test_run_graph_noop():
    graph = bonobo.Graph(bonobo.noop)
    assert len(graph) == 1

    with patch("bonobo._api._is_interactive_console", side_effect=lambda: False):
        result = bonobo.run(graph)

    assert isinstance(result, GraphExecutionContext)
