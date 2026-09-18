from __future__ import annotations

from pathlib import Path

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_shout_audit import REUSED, render_audit
from skyrim_wayfinder.domain import GeographyType, TaskStatus


def test_complete_official_shout_scope(content):
    assert len(content.shouts) == 27
    assert all(len(item.words) == 3 for item in content.shouts.values())
    assert sum(len(item.words) for item in content.shouts.values()) == 81
    assert {item.content_source.value for item in content.shouts.values()} == {
        "SKYRIM", "DAWNGUARD", "DRAGONBORN"
    }


def test_every_credit_has_valid_physical_or_locationless_task(content):
    assert len({item.task_id for item in content.shout_credits.values()}) == 71
    for credit in content.shout_credits.values():
        task = content.tasks[credit.task_id]
        if task.geography_type is GeographyType.PHYSICAL:
            assert task.location_id in content.locations
        else:
            assert task.location_id is None


def test_variable_word_walls_do_not_claim_static_word_identity(content):
    variable = [
        content.tasks[item.task_id] for item in content.shout_credits.values()
        if item.credit_count == 1 and content.tasks[item.task_id].id.startswith("shout_")
        and content.tasks[item.task_id].location_id
        and "battle_fury" not in item.task_id
        and "bend_will" not in item.task_id
        and item.shout_id != "unrelenting_force"
    ]
    assert variable
    assert all("Learn a word of" in task.title for task in variable)


def test_one_credit_and_three_credit_progress(service):
    assert service.shout_progress("aura_whisper") == (0, 3)
    service.set_task_state("shout_aura_whisper_northwind_summit", TaskStatus.COMPLETE)
    assert service.shout_progress("aura_whisper") == (1, 3)
    service.set_task_state("mq_throat_clear_skies", TaskStatus.COMPLETE)
    assert service.shout_progress("clear_skies") == (3, 3)


def test_wall_visitation_order_has_same_final_progress(service):
    first = ("shout_aura_whisper_northwind_summit", "shout_aura_whisper_valthume")
    for task_id in first:
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.shout_progress("aura_whisper") == (2, 3)
    for task_id in first:
        service.set_task_state(task_id, None)
    for task_id in reversed(first):
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.shout_progress("aura_whisper") == (2, 3)


def test_call_dragon_only_credits_completed_adviser(service):
    service.set_task_state("mq_fallen_plan_arngeir", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.shout_progress("call_dragon") == (3, 3)
    assert service.evaluate("mq_fallen_plan_esbern").status is TaskStatus.NOT_APPLICABLE
    assert service.state.get_task_state("mq_fallen_plan_esbern") is None
    assert not any(
        item.task_id == "mq_fallen_capture_odahviing"
        for item in service.content.shout_credits.values()
    )


def test_access_condition_gates_planner_without_changing_denominator(service):
    task_id = "shout_disarm_snow_veil_sanctum"
    assert service.evaluate(task_id).status is TaskStatus.LOCKED
    assert task_id not in {
        entry.task.id for card in service.regional_plan("windhelm") for entry in card.tasks
    }
    before = service.shout_domain_progress()
    service.set_access_condition("access_snow_veil_sanctum", True)
    assert service.evaluate(task_id).status is TaskStatus.AVAILABLE
    assert task_id in {
        entry.task.id for card in service.regional_plan("windhelm") for entry in card.tasks
    }
    assert service.shout_domain_progress() == before


def test_reused_main_tasks_are_not_duplicated(content):
    credited = {item.task_id for item in content.shout_credits.values()}
    assert REUSED <= credited
    assert len(REUSED) == 13
    assert len(credited - REUSED) == 58


def test_all_acquisitions_reach_exactly_81_credits(service):
    for credit in service.content.shout_credits.values():
        if credit.task_id in {
            "mq_fallen_plan_paarthurnax", "mq_fallen_plan_esbern"
        }:
            continue
        service.set_task_state(credit.task_id, TaskStatus.COMPLETE, confirm_choice=True)
    assert service.shout_domain_progress() == (81, 81)


def test_shout_audit_matches_canonical_data():
    root = Path(loader_module.__file__).parents[3]
    assert (root / "docs" / "shout-task-audit.md").read_text(encoding="utf-8") == render_audit()
