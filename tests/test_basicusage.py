import pytest

import bonobo as bb


@pytest.mark.timeout(2)
def test_run_graph_noop():
    graph = bb.Graph(bb.noop)
    assert len(graph) == 1

    result = bb.run(graph, strategy='threadpool')
    assert result
