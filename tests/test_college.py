from __future__ import annotations

from pathlib import Path

import pytest

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_college_audit import render_audit
from skyrim_wayfinder.domain import CompletionRole, PlannerBehavior, StoryClassification, TaskStatus
from skyrim_wayfinder.services import TaskOutcomeRequired


def regional_task_ids(service, region_id: str) -> set[str]:
    return {
        evaluation.task.id
        for card in service.regional_plan(region_id)
        for evaluation in card.tasks
    }


def test_college_story_scope_and_core_denominator(content):
    stories = [item for item in content.stories.values() if item.collection_id == "college_winterhold"]
    assert len(stories) == 18
    assert sum(item.classification is StoryClassification.REQUIRED for item in stories) == 8
    assert sum(item.classification is StoryClassification.OPTIONAL for item in stories) == 10
    core = {
        membership.task_id
        for membership in content.memberships.values()
        if content.stories[membership.story_id].collection_id == "college_winterhold"
        and content.stories[membership.story_id].classification is StoryClassification.REQUIRED
        and membership.completion_role is CompletionRole.REQUIRED
    }
    assert len(core) == 18


def test_main_progression_does_not_surface_later_work(service):
    assert service.evaluate("college_under_saarthal").status is TaskStatus.LOCKED
    assert service.evaluate("college_hitting_books_accept").status is TaskStatus.LOCKED
    assert service.evaluate("college_revealing_unseen_mzulft").status is TaskStatus.LOCKED
    assert service.evaluate("college_staff_magnus").status is TaskStatus.LOCKED
    assert service.evaluate("college_eye_breach_barrier").status is TaskStatus.LOCKED
    service.set_task_state("college_first_lessons", TaskStatus.COMPLETE)
    assert service.evaluate("college_under_saarthal").status is TaskStatus.AVAILABLE


def test_saarthal_access_is_quest_derived_and_manual_override_survives(service):
    condition = "access_saarthal"
    shout = "shout_ice_form_saarthal"
    assert service.evaluate(shout).status is TaskStatus.LOCKED
    service.set_task_state("college_first_lessons", TaskStatus.COMPLETE)
    assert service.is_access_condition_satisfied(condition)
    assert not service.state.is_access_condition_satisfied(condition)
    assert service.evaluate(shout).status is TaskStatus.AVAILABLE
    saarthal = next(card for card in service.regional_plan("winterhold") if card.id == "saarthal")
    assert {"college_under_saarthal", shout} <= {item.task.id for item in saarthal.tasks}
    service.set_access_condition(condition, True)
    service.set_task_state("college_first_lessons", None)
    assert service.state.is_access_condition_satisfied(condition)
    assert service.evaluate(shout).status is TaskStatus.AVAILABLE


def test_mzulft_requires_real_college_acceptance(service):
    task_id = "college_revealing_unseen_mzulft"
    assert service.evaluate(task_id).status is TaskStatus.LOCKED
    service.set_task_state("college_revealing_unseen_accept", TaskStatus.COMPLETE)
    assert service.evaluate(task_id).status is TaskStatus.AVAILABLE
    assert task_id in regional_task_ids(service, "windhelm")


def test_labyrinthian_bundles_college_mask_shout_and_spell(service):
    expected = {
        "college_staff_magnus",
        "mask_morokei",
        "shout_slow_time_labyrinthian",
        "spell_equilibrium_labyrinthian",
    }
    assert all(service.evaluate(task_id).status is TaskStatus.LOCKED for task_id in expected)
    service.set_task_state("college_staff_magnus_accept", TaskStatus.COMPLETE)
    card = next(card for card in service.regional_plan("labyrinthian") if card.id == "labyrinthian")
    assert expected <= {item.task.id for item in card.tasks}


def test_morokei_and_slow_time_are_not_required_for_college(service):
    staff_memberships = [
        item for item in service.content.memberships.values()
        if item.story_id == "college_staff_magnus"
    ]
    roles = {item.task_id: item.completion_role for item in staff_memberships}
    assert roles["college_staff_magnus"] is CompletionRole.REQUIRED
    assert roles["mask_morokei"] is CompletionRole.ASSOCIATED
    assert roles["shout_slow_time_labyrinthian"] is CompletionRole.ASSOCIATED
    assert roles["spell_equilibrium_labyrinthian"] is CompletionRole.ASSOCIATED
    assert any(
        item.task_id == "mask_morokei" and item.story_id == "mask_labyrinthian"
        and item.completion_role is CompletionRole.REQUIRED
        for item in service.content.memberships.values()
    )


def test_staff_progression_preserves_existing_secondary_membership(content):
    memberships = [item for item in content.memberships.values() if item.task_id == "college_staff_magnus"]
    assert {item.story_id for item in memberships} == {"college_staff_magnus", "artifact_staff_magnus"}
    assert "college_staff_magnus" not in content.collectibles


def test_optional_stories_do_not_block_core_completion(service):
    core = {
        membership.task_id
        for membership in service.content.memberships.values()
        if service.content.stories[membership.story_id].collection_id == "college_winterhold"
        and service.content.stories[membership.story_id].classification is StoryClassification.REQUIRED
        and membership.completion_role is CompletionRole.REQUIRED
    }
    for task_id in core:
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.collection_progress("college_winterhold") == (18, 18)
    assert service.state.get_task_state("college_arniel_receive_shade") is None
    assert service.state.get_task_state("college_ritual_alteration_dragonhide") is None


def test_exact_nine_unique_spells_share_acquisition_state(service):
    stories = [item for item in service.content.stories.values() if item.collection_id == "unique_spells"]
    assert len(stories) == 9
    memberships = [
        next(item for item in service.content.memberships.values() if item.story_id == story.id)
        for story in stories
    ]
    assert len({item.task_id for item in memberships}) == 9
    task_id = "college_ritual_illusion_vision"
    service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.story_progress("spell_vision_tenth_eye") == (1, 1)
    assert service.story_progress("college_ritual_illusion")[0] == 1
    assert service.state.all_task_states() == {task_id: TaskStatus.COMPLETE}


def test_ritual_unlocks_are_manual_nonregional_milestones(content):
    expected = {
        "alteration": "90", "conjuration": "90", "destruction": "100",
        "illusion": "100", "restoration": "90",
    }
    for school, level in expected.items():
        task = content.tasks[f"college_ritual_{school}_unlock"]
        assert task.planner_behavior is PlannerBehavior.MILESTONE
        assert task.location_id is None
        assert level in task.objective
        assert not any(item.type == "minimum_level" for item in task.prerequisites)


def test_repeatable_college_jobs_are_excluded(content):
    forbidden = {
        "out_of_balance", "enchanting_pick_up", "restocking_soul_gems", "aftershock",
        "rejoining_college", "tolfdir_absent_minded", "fetch_me_that_book", "shalidors_insights",
    }
    college_ids = {
        item.task_id for item in content.memberships.values()
        if content.stories[item.story_id].collection_id == "college_winterhold"
    }
    assert all(not any(fragment in task_id for fragment in forbidden) for task_id in college_ids)


def test_forgotten_names_is_optional_unjournaled_observed_outcome(service):
    story = service.content.stories["college_forgotten_names"]
    assert story.classification is StoryClassification.OPTIONAL
    task = service.content.tasks["college_forgotten_resolve"]
    assert "unjournaled" in (task.warning_text or "").lower()
    with pytest.raises(TaskOutcomeRequired):
        service.set_task_state(task.id, TaskStatus.COMPLETE)
    service.set_task_state(task.id, TaskStatus.COMPLETE, outcome_id="released")
    assert service.state.get_task_outcome(task.id) == "released"


def test_three_ritual_locations_are_verified(content):
    expected = {
        "windward_ruins": "dawnstar",
        "north_skybound_watch": "falkreath",
        "four_skull_lookout": "markarth",
    }
    for location_id, region_id in expected.items():
        location = content.locations[location_id]
        assert location.region_id == region_id
        assert location.location_type.value == "EXTERIOR_SITE"
        assert location.verification_status.value == "VERIFIED"


def test_college_audit_matches_canonical_graph():
    root = Path(loader_module.__file__).parents[3]
    assert (root / "docs" / "college-task-audit.md").read_text(encoding="utf-8") == render_audit()
