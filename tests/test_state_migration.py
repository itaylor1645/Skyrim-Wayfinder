from __future__ import annotations

import sqlite3

from skyrim_wayfinder.domain import TaskStatus
from skyrim_wayfinder.persistence import StateRepository


def legacy_database(path, rows, current_region="remote_special", version=1):
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE schema_version (version INTEGER NOT NULL);
        INSERT INTO schema_version VALUES (1);
        CREATE TABLE task_state (
            task_id TEXT PRIMARY KEY,
            state TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE choices (
            choice_id TEXT PRIMARY KEY,
            option_id TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """
    )
    connection.execute("UPDATE schema_version SET version = ?", (version,))
    connection.executemany("INSERT INTO task_state(task_id, state) VALUES (?, ?)", rows)
    connection.execute("INSERT INTO settings(key, value) VALUES ('current_region', ?)", (current_region,))
    connection.commit()
    connection.close()


def test_completed_composite_marks_all_atomic_replacements_complete(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    legacy_database(path, [("college_revealing_unseen", "COMPLETE")], "college_winterhold")
    repository = StateRepository(path)
    assert repository.get_task_state("college_revealing_unseen") is None
    assert repository.get_task_state("college_revealing_unseen_mzulft") is TaskStatus.COMPLETE
    assert repository.get_task_state("college_revealing_unseen_report_college") is TaskStatus.COMPLETE
    assert repository.current_region == "winterhold"
    repository.close()


def test_noncomplete_composite_state_is_discarded_and_remote_region_cleared(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    legacy_database(path, [("db_innocence_lost", "DEFERRED")])
    repository = StateRepository(path)
    assert repository.get_task_state("db_innocence_lost") is None
    assert repository.get_task_state("db_innocence_lost_kill_grelod") is None
    assert repository.get_task_state("db_innocence_lost_report_aventus") is None
    assert repository.current_region is None
    repository.close()


def test_new_explicit_prerequisite_is_inferred_without_overwriting_other_state(tmp_path):
    path = tmp_path / "v2.sqlite3"
    legacy_database(
        path,
        [
            ("db_innocence_lost_kill_grelod", "COMPLETE"),
            ("db_innocence_lost_report_aventus", "DEFERRED"),
        ],
        current_region="riften",
        version=2,
    )
    repository = StateRepository(path)
    assert repository.get_task_state("db_innocence_lost_speak_aventus") is TaskStatus.COMPLETE
    assert repository.get_task_state("db_innocence_lost_kill_grelod") is TaskStatus.COMPLETE
    assert repository.get_task_state("db_innocence_lost_report_aventus") is TaskStatus.DEFERRED
    repository.close()


def test_retired_fallen_milestone_is_reset_without_inference(tmp_path):
    path = tmp_path / "v3.sqlite3"
    legacy_database(
        path,
        [("mq_the_fallen_milestone", "COMPLETE")],
        current_region="whiterun",
        version=3,
    )
    repository = StateRepository(path)
    assert repository.get_task_state("mq_the_fallen_milestone") is None
    assert repository.get_task_state("mq_fallen_ask_jarl") is None
    assert repository.get_choice("mq_fallen_adviser") is None
    assert repository.all_task_outcomes() == {}
    repository.close()
