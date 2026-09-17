from skyrim_wayfinder.domain import TaskStatus
from skyrim_wayfinder.persistence import StateRepository
from skyrim_wayfinder.services import WayfinderService


def test_completion_persists_after_database_reload(tmp_path, content):
    path = tmp_path / "state.sqlite3"
    first_repo = StateRepository(path, content.fingerprint)
    first = WayfinderService(content, first_repo)
    first.set_task_state("college_first_lessons", TaskStatus.COMPLETE)
    first_repo.close()
    second_repo = StateRepository(path, content.fingerprint)
    second = WayfinderService(content, second_repo)
    assert second.evaluate("college_first_lessons").status is TaskStatus.COMPLETE
    second_repo.close()


def test_settings_and_choice_persist(tmp_path, content):
    path = tmp_path / "state.sqlite3"
    repo = StateRepository(path, content.fingerprint)
    repo.player_level = 18
    repo.current_region = "riften"
    repo.set_choice("dark_brotherhood_path", "destroy")
    repo.close()
    reopened = StateRepository(path, content.fingerprint)
    assert reopened.player_level == 18
    assert reopened.current_region == "riften"
    assert reopened.get_choice("dark_brotherhood_path") == "destroy"
    reopened.close()
