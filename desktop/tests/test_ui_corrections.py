"""One test per interface defect of the status report."""
from conftest import Driver


def _match(name="escenario_general_p_tardo.json"):
    d = Driver()
    d.load(name)
    d.store.calculate_plan()
    d.go("simulacion")
    return d


def test_cancelling_the_native_dialog_closes_it_without_errors(monkeypatch):
    monkeypatch.setattr("tardo_ui.filepicker.choose_native", lambda start=None: (True, None))
    d = Driver()
    d.click("Seleccionar archivo")
    d.frame()
    assert d.app.picker is None and d.store.scenario is None and d.app.running


def test_a_file_chosen_in_the_native_dialog_is_loaded(monkeypatch):
    from conftest import DOCS
    chosen = DOCS / "escenario_puentes.json"
    monkeypatch.setattr("tardo_ui.filepicker.choose_native", lambda start=None: (True, chosen))
    d = Driver()
    d.click("Seleccionar archivo")
    d.frame()
    assert d.store.scenario is not None and d.app.picker is None


def test_every_bought_soldier_can_be_selected():
    d = _match()
    for _ in range(14):
        d.store.recruit("infantry")
    d.frame()
    seen = set()
    for _ in range(3):
        seen |= {k for k in d.hits if k.startswith("soldado:")}
        d.click("soldados:next")
    assert len(seen) == 14
    assert "soldado:S13" in d.hits
    d.click("soldado:S13")
    assert d.store.picked == ["S13"]


def test_every_position_can_be_chosen_as_destination():
    d = _match("escenario_gran_ciudadela.json")
    seen = set()
    for _ in range(4):
        seen |= {k[5:] for k in d.hits if k.startswith("dest:")}
        d.click("destinos:next")
    assert seen == {v["id"] for v in d.store.scenario["graph_e"]["vertices"]}


def test_clicking_a_position_on_the_map_chooses_it_as_destination():
    d = _match()
    vertex = next(v for v in d.store.scenario["graph_e"]["vertices"] if v["id"] == "V_H1")
    d.click_at(d.app.ui.viewport.to_screen(vertex["coords"]))
    assert d.store.dest == "V_H1"


def test_all_corridors_can_be_consulted():
    d = _match("escenario_gran_ciudadela.json")
    d.click("pestaña:corredores")
    wanted = {c["id"] for c in d.store.scenario["graph_m"]["corridors"]}
    seen = set()
    for _ in range(3):
        seen |= wanted & set(d.texts())
        if "corredores:next" in d.hits:
            d.click("corredores:next")
    assert seen == wanted


def test_the_greedy_explanation_stays_inside_its_panel():
    d = Driver()
    d.load("escenario_gran_ciudadela.json")
    d.store.calculate_plan()
    d.go("plan")
    seen = []
    for _ in range(6):
        seen += d.texts()
        if "pasos:next" in d.hits:
            d.click("pasos:next")
    for step in d.store.plan["steps"]:
        assert any(text.startswith(f"Iteración {step['iteration']}:") for text in seen)


def test_orders_are_disabled_once_the_match_ends():
    d = _match()
    d.play_to_end()
    d.store.hide_end = True
    d.frame()
    budget = d.store.sim["budget"]["available"]
    d.click("Infantería")
    assert d.store.sim["budget"]["available"] == budget and d.store.sim["soldiers"] == []
