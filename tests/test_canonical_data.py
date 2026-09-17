from skyrim_wayfinder.data import load_canonical_content
from skyrim_wayfinder.persistence import StateRepository


def test_canonical_seed_load_is_reproducible(tmp_path):
    first = load_canonical_content()
    second = load_canonical_content()
    assert first.fingerprint == second.fingerprint
    assert first.tasks == second.tasks
    one = StateRepository(tmp_path / "one.sqlite3", first.fingerprint)
    two = StateRepository(tmp_path / "two.sqlite3", second.fingerprint)
    assert one.get_setting("canonical_fingerprint") == two.get_setting("canonical_fingerprint")
    assert one.all_task_states() == two.all_task_states() == {}
    one.close()
    two.close()


def test_stable_string_ids_and_references(content):
    assert len(content.tasks) == 38
    assert all(isinstance(task_id, str) and " " not in task_id for task_id in content.tasks)
    assert content.tasks["college_staff_magnus"].location_id == "labyrinthian"
    assert content.locations["labyrinthian"].region_id == "labyrinthian"
