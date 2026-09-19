from __future__ import annotations

from pathlib import Path

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_companions_audit import REUSED, render_audit
from skyrim_wayfinder.domain import CompletionRole, PlannerBehavior, StoryClassification, TaskStatus


def regional_task_ids(service, region_id: str) -> set[str]:
    return {
        evaluation.task.id
        for card in service.regional_plan(region_id)
        for evaluation in card.tasks
    }


def test_companions_story_scope_and_core_denominator(content):
    stories = [item for item in content.stories.values() if item.collection_id == "companions"]
    assert len(stories) == 9
    assert sum(item.classification is StoryClassification.REQUIRED for item in stories) == 6
    assert sum(item.classification is StoryClassification.OPTIONAL for item in stories) == 3
    required = {
        membership.task_id
        for membership in content.memberships.values()
        if content.stories[membership.story_id].collection_id == "companions"
        and content.stories[membership.story_id].classification is StoryClassification.REQUIRED
        and membership.completion_role is CompletionRole.REQUIRED
    }
    assert len(required) == 24


def test_progression_and_four_radiant_milestones_unlock_in_order(service):
    assert service.evaluate("companions_gate_job_after_take").status is TaskStatus.LOCKED
    assert service.evaluate("companions_proving_accept").status is TaskStatus.LOCKED
    service.set_task_state("companions_take_finish_errands", TaskStatus.COMPLETE)
    assert service.evaluate("companions_gate_job_after_take").status is TaskStatus.AVAILABLE
    service.set_task_state("companions_gate_job_after_take", TaskStatus.COMPLETE)
    assert service.evaluate("companions_proving_accept").status is TaskStatus.AVAILABLE

    milestones = {
        "companions_gate_job_after_take",
        "companions_gate_job_after_proving",
        "companions_gate_aela_retaliation",
        "companions_gate_second_retaliation",
    }
    assert all(service.content.tasks[item].planner_behavior is PlannerBehavior.MILESTONE for item in milestones)
    assert milestones.isdisjoint(
        task_id for region_id in service.content.regions for task_id in regional_task_ids(service, region_id)
    )


def test_repeatable_radiants_are_not_catalog_tasks(content):
    forbidden = {
        "animal_extermination", "hired_muscle", "trouble_in_skyrim", "family_heirloom",
        "escaped_criminal", "rescue_mission", "striking_the_heart", "stealing_plans",
        "dragon_seekers", "animal_pelt_collection",
    }
    companion_task_ids = {
        membership.task_id
        for membership in content.memberships.values()
        if content.stories[membership.story_id].collection_id == "companions"
    }
    assert all(not any(name in task_id for name in forbidden) for task_id in companion_task_ids)


def test_dustmans_access_derives_from_real_progress_and_preserves_manual_override(service):
    shout_id = "shout_fire_breath_dustmans_cairn"
    assert service.evaluate(shout_id).status is TaskStatus.LOCKED
    assert not service.state.is_access_condition_satisfied("access_dustmans_cairn")
    service.set_task_state("companions_proving_accept", TaskStatus.COMPLETE)
    assert service.is_access_condition_satisfied("access_dustmans_cairn")
    assert not service.state.is_access_condition_satisfied("access_dustmans_cairn")
    assert service.evaluate(shout_id).status is TaskStatus.AVAILABLE
    dustmans = next(card for card in service.regional_plan("whiterun") if card.id == "dustmans_cairn")
    assert {"companions_proving_recover_fragment", shout_id} <= {
        item.task.id for item in dustmans.tasks
    }

    service.set_access_condition("access_dustmans_cairn", True)
    service.set_task_state("companions_proving_accept", None)
    assert service.state.is_access_condition_satisfied("access_dustmans_cairn")
    assert service.evaluate(shout_id).status is TaskStatus.AVAILABLE


def test_ysgramors_access_derives_from_wuuthrad_and_aggregates_shout(service):
    shout_id = "shout_animal_allegiance_ysgramors_tomb"
    assert service.evaluate(shout_id).status is TaskStatus.LOCKED
    service.set_task_state("companions_glory_receive_wuuthrad", TaskStatus.COMPLETE)
    assert service.is_access_condition_satisfied("access_ysgramors_tomb")
    assert service.evaluate(shout_id).status is TaskStatus.AVAILABLE
    tomb = next(card for card in service.regional_plan("winterhold") if card.id == "ysgramors_tomb")
    assert {"companions_glory_open_tomb", shout_id} <= {item.task.id for item in tomb.tasks}


def test_shout_tasks_are_reused_as_associated_memberships(content):
    assert REUSED <= content.tasks.keys()
    for task_id in REUSED:
        memberships = [item for item in content.memberships.values() if item.task_id == task_id]
        companions = [
            item for item in memberships
            if content.stories[item.story_id].collection_id == "companions"
        ]
        assert len(companions) == 1
        assert companions[0].completion_role is CompletionRole.ASSOCIATED
        assert not companions[0].is_primary


def test_optional_stories_and_word_walls_do_not_block_core_completion(service):
    core_required = {
        membership.task_id
        for membership in service.content.memberships.values()
        if service.content.stories[membership.story_id].collection_id == "companions"
        and service.content.stories[membership.story_id].classification is StoryClassification.REQUIRED
        and membership.completion_role is CompletionRole.REQUIRED
    }
    for task_id in core_required:
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.collection_progress("companions") == (24, 24)
    assert all(service.state.get_task_state(task_id) is None for task_id in REUSED)
    assert service.state.get_task_state("companions_totem_place_1") is None
    assert service.state.get_task_state("companions_purity_farkas_cure") is None


def test_lycanthropy_current_state_does_not_rewrite_historical_progress(service):
    ritual = "companions_silver_become_werewolf"
    service.set_task_state(ritual, TaskStatus.COMPLETE)
    assert service.is_access_condition_satisfied("companions_lycanthropy_active")
    assert service.evaluate("companions_totem_retrieve_1").status is TaskStatus.LOCKED
    service.set_task_state("companions_glory_free_kodlak", TaskStatus.COMPLETE)
    assert service.evaluate("companions_totem_retrieve_1").status is TaskStatus.AVAILABLE
    service.set_task_state("prep_companions_player_witch_head", TaskStatus.COMPLETE)
    service.set_task_state("companions_glory_cure_player", TaskStatus.COMPLETE)
    assert not service.is_access_condition_satisfied("companions_lycanthropy_active")
    assert service.evaluate(ritual).status is TaskStatus.COMPLETE
    assert service.evaluate("companions_totem_retrieve_1").status is TaskStatus.LOCKED
    service.set_access_condition("companions_lycanthropy_active", True)
    assert service.evaluate("companions_totem_retrieve_1").status is TaskStatus.AVAILABLE


def test_personal_purification_access_has_immediate_and_later_paths(service):
    condition_id = "access_companions_personal_purification"
    service.set_task_state("companions_glory_free_kodlak", TaskStatus.COMPLETE)
    assert service.state.is_access_condition_satisfied(condition_id)
    service.set_access_condition(condition_id, False)  # player left the immediate opportunity
    assert not service.is_access_condition_satisfied(condition_id)
    service.set_task_state("companions_purity_farkas_cure", TaskStatus.COMPLETE)
    assert not service.is_access_condition_satisfied(condition_id)
    service.set_task_state("companions_purity_vilkas_cure", TaskStatus.COMPLETE)
    assert service.is_access_condition_satisfied(condition_id)


def test_skyforge_is_verified_whiterun_geography(content):
    skyforge = content.locations["skyforge"]
    assert skyforge.region_id == "whiterun"
    assert skyforge.location_type.value == "EXTERIOR_SITE"
    assert skyforge.verification_status.value == "VERIFIED"


def test_companions_audit_matches_canonical_graph():
    root = Path(loader_module.__file__).parents[3]
    assert (root / "docs" / "companions-task-audit.md").read_text(encoding="utf-8") == render_audit()
