from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from skyrim_wayfinder.domain import TaskStatus


def default_database_path() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return root / "SkyrimWayfinder" / "wayfinder.sqlite3"


class StateRepository:
    """SQLite-backed user intent. Canonical game definitions never live here."""

    def __init__(self, path: str | Path, canonical_fingerprint: str = "") -> None:
        self.path = Path(path) if str(path) != ":memory:" else Path(":memory:")
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self._migrate()
        if canonical_fingerprint:
            self.set_setting("canonical_fingerprint", canonical_fingerprint)

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            );
            INSERT INTO schema_version(version)
                SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM schema_version);
            CREATE TABLE IF NOT EXISTS task_state (
                task_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS choices (
                choice_id TEXT PRIMARY KEY,
                option_id TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS task_outcomes (
                task_id TEXT PRIMARY KEY,
                outcome_id TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS access_condition_state (
                condition_id TEXT PRIMARY KEY,
                satisfied INTEGER NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        version = int(self.connection.execute("SELECT version FROM schema_version LIMIT 1").fetchone()[0])
        if version < 2:
            self._migrate_to_v2()
        if version < 3:
            self._migrate_to_v3()
        if version < 4:
            self._migrate_to_v4()
        if version < 5:
            self.connection.execute("UPDATE schema_version SET version = 5")
        self.connection.commit()

    def _migrate_to_v2(self) -> None:
        """Migrate pre-production prototype state to the atomic location schema."""
        split_tasks = {
            "college_revealing_unseen": (
                "college_revealing_unseen_mzulft",
                "college_revealing_unseen_report_college",
            ),
            "college_containment": (
                "college_containment_defend_winterhold",
                "college_containment_report_college",
            ),
            "db_innocence_lost": (
                "db_innocence_lost_kill_grelod",
                "db_innocence_lost_report_aventus",
            ),
        }
        for old_id, replacement_ids in split_tasks.items():
            row = self.connection.execute(
                "SELECT state FROM task_state WHERE task_id = ?", (old_id,)
            ).fetchone()
            if row and row["state"] == TaskStatus.COMPLETE.value:
                for replacement_id in replacement_ids:
                    self.connection.execute(
                        "INSERT OR REPLACE INTO task_state(task_id, state) VALUES (?, ?)",
                        (replacement_id, TaskStatus.COMPLETE.value),
                    )
            self.connection.execute("DELETE FROM task_state WHERE task_id = ?", (old_id,))

        region_map = {
            "riverwood": "whiterun",
            "college_winterhold": "winterhold",
            "high_hrothgar": "high_hrothgar",
            "labyrinthian": "labyrinthian",
            "whiterun": "whiterun",
            "riften": "riften",
            "markarth": "markarth",
        }
        current = self.connection.execute(
            "SELECT value FROM settings WHERE key = 'current_region'"
        ).fetchone()
        if current:
            mapped = region_map.get(current["value"])
            if mapped:
                self.connection.execute(
                    "UPDATE settings SET value = ? WHERE key = 'current_region'", (mapped,)
                )
            else:
                self.connection.execute("DELETE FROM settings WHERE key = 'current_region'")
        self.connection.execute("UPDATE schema_version SET version = 2")

    def _migrate_to_v3(self) -> None:
        """Backfill newly explicit quest-start steps only when later work is complete."""
        inferred_steps = {
            "db_innocence_lost_speak_aventus": (
                "db_innocence_lost_kill_grelod",
                "db_innocence_lost_report_aventus",
            ),
            "college_gain_admission": ("college_first_lessons",),
            "riften_stoking_flames_start": ("riften_deliver_fire_salts",),
            "db_trigger_abduction_sleep": ("db_join_at_shack", "db_destroy_at_shack"),
        }
        for new_id, downstream_ids in inferred_steps.items():
            placeholders = ",".join("?" for _ in downstream_ids)
            row = self.connection.execute(
                f"SELECT 1 FROM task_state WHERE task_id IN ({placeholders}) AND state = ? LIMIT 1",
                (*downstream_ids, TaskStatus.COMPLETE.value),
            ).fetchone()
            if row:
                self.connection.execute(
                    "INSERT OR REPLACE INTO task_state(task_id, state) VALUES (?, ?)",
                    (new_id, TaskStatus.COMPLETE.value),
                )
        selected_path = self.connection.execute(
            "SELECT 1 FROM choices WHERE choice_id = 'dark_brotherhood_path' LIMIT 1"
        ).fetchone()
        if selected_path:
            self.connection.execute(
                "INSERT OR REPLACE INTO task_state(task_id, state) VALUES (?, ?)",
                ("db_trigger_abduction_sleep", TaskStatus.COMPLETE.value),
            )
        self.connection.execute("UPDATE schema_version SET version = 3")

    def _migrate_to_v4(self) -> None:
        """Retire the prototype Main Quest bridge without inferring branch history."""
        self.connection.execute(
            "DELETE FROM task_state WHERE task_id = 'mq_the_fallen_milestone'"
        )
        self.connection.execute("UPDATE schema_version SET version = 4")

    def close(self) -> None:
        self.connection.close()

    def get_task_state(self, task_id: str) -> TaskStatus | None:
        row = self.connection.execute(
            "SELECT state FROM task_state WHERE task_id = ?", (task_id,)
        ).fetchone()
        return TaskStatus(row["state"]) if row else None

    def all_task_states(self) -> dict[str, TaskStatus]:
        return {
            row["task_id"]: TaskStatus(row["state"])
            for row in self.connection.execute("SELECT task_id, state FROM task_state")
        }

    def set_task_state(self, task_id: str, state: TaskStatus) -> None:
        self.connection.execute(
            """INSERT INTO task_state(task_id, state) VALUES (?, ?)
               ON CONFLICT(task_id) DO UPDATE SET state=excluded.state,
               updated_at=CURRENT_TIMESTAMP""",
            (task_id, state.value),
        )
        self.connection.commit()

    def reset_task_state(self, task_id: str) -> None:
        self.connection.execute("DELETE FROM task_state WHERE task_id = ?", (task_id,))
        self.connection.commit()

    def get_choice(self, choice_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT option_id FROM choices WHERE choice_id = ?", (choice_id,)
        ).fetchone()
        return row["option_id"] if row else None

    def set_choice(self, choice_id: str, option_id: str) -> None:
        self.connection.execute(
            """INSERT INTO choices(choice_id, option_id) VALUES (?, ?)
               ON CONFLICT(choice_id) DO UPDATE SET option_id=excluded.option_id,
               updated_at=CURRENT_TIMESTAMP""",
            (choice_id, option_id),
        )
        self.connection.commit()

    def reset_choice(self, choice_id: str, option_id: str | None = None) -> None:
        if option_id is None:
            self.connection.execute("DELETE FROM choices WHERE choice_id = ?", (choice_id,))
        else:
            self.connection.execute(
                "DELETE FROM choices WHERE choice_id = ? AND option_id = ?",
                (choice_id, option_id),
            )
        self.connection.commit()

    def all_choices(self) -> dict[str, str]:
        return {
            row["choice_id"]: row["option_id"]
            for row in self.connection.execute("SELECT choice_id, option_id FROM choices")
        }

    def get_task_outcome(self, task_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT outcome_id FROM task_outcomes WHERE task_id = ?", (task_id,)
        ).fetchone()
        return row["outcome_id"] if row else None

    def set_task_outcome(self, task_id: str, outcome_id: str) -> None:
        self.connection.execute(
            """INSERT INTO task_outcomes(task_id, outcome_id) VALUES (?, ?)
               ON CONFLICT(task_id) DO UPDATE SET outcome_id=excluded.outcome_id,
               updated_at=CURRENT_TIMESTAMP""",
            (task_id, outcome_id),
        )
        self.connection.commit()

    def reset_task_outcome(self, task_id: str) -> None:
        self.connection.execute("DELETE FROM task_outcomes WHERE task_id = ?", (task_id,))
        self.connection.commit()

    def all_task_outcomes(self) -> dict[str, str]:
        return {
            row["task_id"]: row["outcome_id"]
            for row in self.connection.execute("SELECT task_id, outcome_id FROM task_outcomes")
        }

    def is_access_condition_satisfied(self, condition_id: str) -> bool:
        row = self.connection.execute(
            "SELECT satisfied FROM access_condition_state WHERE condition_id = ?", (condition_id,)
        ).fetchone()
        return bool(row["satisfied"]) if row else False

    def set_access_condition(self, condition_id: str, satisfied: bool) -> None:
        if not satisfied:
            self.connection.execute(
                "DELETE FROM access_condition_state WHERE condition_id = ?", (condition_id,)
            )
        else:
            self.connection.execute(
                """INSERT INTO access_condition_state(condition_id, satisfied) VALUES (?, 1)
                   ON CONFLICT(condition_id) DO UPDATE SET satisfied=1, updated_at=CURRENT_TIMESTAMP""",
                (condition_id,),
            )
        self.connection.commit()

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        row = self.connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        self.connection.execute(
            """INSERT INTO settings(key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
            (key, value),
        )
        self.connection.commit()

    @property
    def player_level(self) -> int:
        return int(self.get_setting("player_level", "1") or 1)

    @player_level.setter
    def player_level(self, value: int) -> None:
        self.set_setting("player_level", str(max(1, value)))

    @property
    def current_region(self) -> str | None:
        return self.get_setting("current_region")

    @current_region.setter
    def current_region(self, value: str | None) -> None:
        if value is None:
            self.connection.execute("DELETE FROM settings WHERE key = 'current_region'")
            self.connection.commit()
        else:
            self.set_setting("current_region", value)
