from collections import namedtuple

import bonobo
from bonobo.config import use_raw_input
from bonobo.execution.contexts import GraphExecutionContext
from bonobo.util.bags import BagType

Extracted = namedtuple("Extracted", ["id", "name", "value"])
ExtractedBT = BagType("ExtractedBT", ["id", "name", "value"])


def extract_nt():
    yield Extracted(id=1, name="Guido", value=".py")
    yield Extracted(id=2, name="Larry", value=".pl")
    yield Extracted(id=3, name="Dennis", value=".c")
    yield Extracted(id=4, name="Yukihiro", value=".rb")


def extract_bt():
    yield ExtractedBT(id=1, name="Guido", value=".py")
    yield ExtractedBT(id=2, name="Larry", value=".pl")
    yield ExtractedBT(id=3, name="Dennis", value=".c")
    yield ExtractedBT(id=4, name="Yukihiro", value=".rb")


def transform_using_args(id, name, value):
    yield Extracted(id=id * 2, name=name, value=name.lower() + value)


@use_raw_input
def transform_nt(row):
    yield row._replace(name=row.name.upper())


def StoreInList(buffer: list):
    def store_in_list(*args, buffer=buffer):
        buffer.append(args)

    return store_in_list


def test_execution():
    graph = bonobo.Graph()

    result_args = []
    result_nt = []
    result_bt = []

    graph.add_chain(extract_nt, transform_using_args, StoreInList(result_args))
    graph.add_chain(transform_nt, StoreInList(result_nt), _input=extract_nt)
    graph.add_chain(extract_bt, transform_using_args, StoreInList(result_bt))

    with GraphExecutionContext(graph) as context:
        context.run_until_complete()

    assert result_args == [
        (2, "Guido", "guido.py"),
        (4, "Larry", "larry.pl"),
        (6, "Dennis", "dennis.c"),
        (8, "Yukihiro", "yukihiro.rb"),
    ]

    assert result_nt == [(1, "GUIDO", ".py"), (2, "LARRY", ".pl"), (3, "DENNIS", ".c"), (4, "YUKIHIRO", ".rb")]

    assert result_bt == [
        (2, "Guido", "guido.py"),
        (4, "Larry", "larry.pl"),
        (6, "Dennis", "dennis.c"),
        (8, "Yukihiro", "yukihiro.rb"),
    ]
