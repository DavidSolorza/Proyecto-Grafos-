"""Requirement 12: the user picks the JSON from the interface; the program has no fixed input path."""
import json
from pathlib import Path

from conftest import DOCS
from tardo_ui.filepicker import FilePicker, list_dir


def test_list_dir_shows_folders_then_json_files_and_hides_the_rest(tmp_path):
    (tmp_path / "zeta").mkdir()
    (tmp_path / "Alfa").mkdir()
    (tmp_path / ".oculta").mkdir()
    for name in ("b.json", "A.JSON", "notas.txt", "foto.png"):
        (tmp_path / name).write_text("{}")
    assert list_dir(tmp_path) == [("Alfa", True), ("zeta", True), ("A.JSON", False), ("b.json", False)]


def test_list_dir_survives_unreadable_or_missing_folders(tmp_path):
    assert list_dir(tmp_path / "no_existe") == []


def test_picker_starts_in_a_real_folder_even_if_the_last_one_vanished(tmp_path):
    assert FilePicker(tmp_path / "ya_no_existe").folder == Path.cwd()
    assert FilePicker(tmp_path).folder == tmp_path


def test_choosing_a_scenario_with_the_mouse_loads_and_validates_it(ui):
    ui.click("Seleccionar archivo")
    assert ui.app.picker is not None
    ui.click("ir:Ejemplos del proyecto")
    assert ui.app.picker.folder == DOCS
    ui.click("fila:escenario_complejo.json")
    assert ui.app.picker is None
    assert "complejo" in ui.store.scenario["metadata"]["title"]
    assert ui.app.last_dir == DOCS                              # the dialog remembers where the user was


def test_navigating_into_a_folder_and_back(ui, tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "esc.json").write_text((DOCS / "escenario_puentes.json").read_text(encoding="utf-8"), encoding="utf-8")
    ui.app.last_dir = tmp_path
    ui.click("Seleccionar archivo")
    ui.click("fila:sub/")
    assert ui.app.picker.folder == tmp_path / "sub"
    ui.click("fila:..  (carpeta superior)")
    assert ui.app.picker.folder == tmp_path
    ui.click("fila:sub/")
    ui.click("fila:esc.json")
    assert "puentes" in ui.store.scenario["metadata"]["title"]


def test_an_invalid_file_chosen_in_the_dialog_shows_the_backend_message(ui, tmp_path):
    bad = tmp_path / "roto.json"
    bad.write_text(json.dumps({"metadata": {"D0": 0}}), encoding="utf-8")
    ui.app.last_dir = tmp_path
    ui.click("Seleccionar archivo")
    ui.click("fila:roto.json")
    assert ui.store.scenario is None and ui.store.notice[1] == "error"
    assert "Falta la sección" in ui.store.notice[0]


def test_cancel_closes_the_dialog_without_loading(ui):
    ui.click("Seleccionar archivo")
    ui.click("Cancelar")
    assert ui.app.picker is None and ui.store.scenario is None


def test_scrolling_a_long_folder_never_goes_out_of_range(ui, tmp_path):
    for i in range(80):
        (tmp_path / f"e{i:02}.json").write_text("{}")
    ui.app.last_dir = tmp_path
    ui.click("Seleccionar archivo")
    for _ in range(30):
        ui.wheel((680, 400), -3)
    assert 0 < ui.app.picker.scroll <= 81
    for _ in range(60):
        ui.wheel((680, 400), 3)
    assert ui.app.picker.scroll == 0
