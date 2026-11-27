"""Sections 3, 12 and 13: a badly formed file is always answered with a message, never a crash."""
import copy
import json

import pytest

from conftest import DOCS
from src.app import create_app

JUNK = (None, 5, -1, "x", [], {}, True, [5], ["x"], {"id": []})


def _paths(node, prefix=()):
    """Every position inside the JSON (first element of each list is enough)."""
    children = node.items() if isinstance(node, dict) else enumerate(node[:1]) if isinstance(node, list) else ()
    for key, child in children:
        yield prefix + (key,)
        yield from _paths(child, prefix + (key,))


def _raw():
    return json.loads((DOCS / "escenario_general_p_tardo.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("junk", JUNK, ids=repr)
def test_junk_anywhere_in_the_file_never_causes_a_server_error(junk):
    client = create_app().test_client()
    broken = []
    for path in _paths(_raw()):
        data = _raw()
        target = data
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = copy.deepcopy(junk)
        status = client.post("/api/scenario/upload", json=data).status_code
        if status not in (200, 400):
            broken.append((path, status))
    assert broken == []


@pytest.mark.parametrize("extra", [5, "x", None, []], ids=repr)
@pytest.mark.parametrize("where", ["graph_e.vertices", "graph_e.edges", "graph_m.vertices",
                                   "graph_m.edges", "candidates_meta"])
def test_an_element_that_is_not_an_object_is_explained(where, extra):
    data = _raw()
    target = data
    for key in where.split("."):
        target = target[key]
    target.append(extra)
    response = create_app().test_client().post("/api/scenario/upload", json=data)
    assert response.status_code == 400 and "objetos" in response.get_json()["error"]
