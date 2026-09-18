from __future__ import annotations

from pathlib import Path

import pytest

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_main_quest_audit import render_audit
from skyrim_wayfinder.domain import CompletionRole, RegionType, TaskStatus
from skyrim_wayfinder.services import ChoiceConfirmationRequired, TaskOutcomeRequired


def regional_task_ids(service, region_id: str) -> set[str]:
    return {
        evaluation.task.id
        for item in service.regional_plan(region_id)
        for evaluation in item.tasks
    }


def main_required_task_ids(service) -> set[str]:
    result = set()
    for membership in service.content.memberships.values():
        story = service.content.stories[membership.story_id]
        if (
            story.collection_id == "skyrim_main_quest"
            and membership.completion_role is CompletionRole.REQUIRED
            and story.id not in {"mq_season_unending", "mq_paarthurnax"}
        ):
            result.add(membership.task_id)
    return result


def test_early_main_progression_does_not_gate_independent_cross_domain_work(service):
    assert service.evaluate("mq_bleak_falls_dragonstone").status is TaskStatus.LOCKED
    assert service.evaluate("collectible_golden_claw_recover").status is TaskStatus.AVAILABLE
    assert service.evaluate("shout_unrelenting_force_bleak_falls").status is TaskStatus.AVAILABLE
    service.set_task_state("mq_unbound_escape_helgen", TaskStatus.COMPLETE)
    service.set_task_state("mq_before_storm_go_whiterun", TaskStatus.COMPLETE)
    service.set_task_state("mq_bleak_falls_accept", TaskStatus.COMPLETE)
    assert service.evaluate("mq_bleak_falls_dragonstone").status is TaskStatus.LOCKED
    service.set_task_state("collectible_golden_claw_recover", TaskStatus.COMPLETE)
    assert service.evaluate("mq_bleak_falls_dragonstone").status is TaskStatus.AVAILABLE


def test_multi_location_progression_unlocks_new_region_without_story_geography(service):
    service.set_task_state("mq_horn_search_ustengrav", TaskStatus.COMPLETE)
    assert "mq_horn_meet_delphine" in regional_task_ids(service, "whiterun")
    assert service.content.tasks["mq_horn_search_ustengrav"].location_id == "ustengrav"
    assert service.content.tasks["mq_horn_meet_delphine"].location_id == "sleeping_giant_inn"
    assert not hasattr(service.content.stories["mq_horn_jurgen"], "location_id")


def test_cross_membership_has_one_state_and_updates_both_story_counts(service):
    task_id = "mq_way_voice_whirlwind"
    memberships = service.memberships_for_task(task_id)
    assert {item.story_id for item in memberships} == {"mq_way_voice", "shout_whirlwind_greybeards"}
    service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.story_progress("mq_way_voice")[0] == 1
    assert service.story_progress("shout_whirlwind_greybeards") == (1, 1)
    assert service.state.all_task_states() == {task_id: TaskStatus.COMPLETE}


def test_high_hrothgar_and_blackreach_are_gated_by_real_progression(service):
    assert "mq_way_voice_high_hrothgar" not in regional_task_ids(service, "high_hrothgar")
    service.set_task_state("hold_whiterun_thane", TaskStatus.COMPLETE)
    assert "mq_way_voice_high_hrothgar" in regional_task_ids(service, "high_hrothgar")
    assert "mq_elder_cross_blackreach" not in regional_task_ids(service, "blackreach")
    service.set_task_state("mq_elder_descend_alftand", TaskStatus.COMPLETE)
    assert "mq_elder_cross_blackreach" in regional_task_ids(service, "blackreach")


def test_fallen_any_route_excludes_unused_advisers_and_unlocks_jarl(service):
    service.set_task_state("mq_alduins_bane_defeat", TaskStatus.COMPLETE)
    advisers = {
        "mq_fallen_plan_paarthurnax", "mq_fallen_plan_arngeir", "mq_fallen_plan_esbern"
    }
    assert all(service.evaluate(item).status is TaskStatus.AVAILABLE for item in advisers)
    with pytest.raises(ChoiceConfirmationRequired):
        service.set_task_state("mq_fallen_plan_arngeir", TaskStatus.COMPLETE)
    service.set_task_state("mq_fallen_plan_arngeir", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.evaluate("mq_fallen_ask_jarl").status is TaskStatus.AVAILABLE
    assert all(
        service.evaluate(item).status is TaskStatus.NOT_APPLICABLE
        for item in advisers - {"mq_fallen_plan_arngeir"}
    )
    assert service.story_progress("mq_the_fallen")[1] == 3


def test_jarl_observed_outcome_controls_conditional_season_unending(service):
    service.set_task_state("mq_fallen_plan_arngeir", TaskStatus.COMPLETE, confirm_choice=True)
    with pytest.raises(TaskOutcomeRequired):
        service.set_task_state("mq_fallen_ask_jarl", TaskStatus.COMPLETE)
    assert service.story_progress("mq_season_unending") == (0, 0)
    service.set_task_state(
        "mq_fallen_ask_jarl", TaskStatus.COMPLETE, outcome_id="truce_required"
    )
    assert service.evaluate("mq_season_ask_arngeir").status is TaskStatus.AVAILABLE
    assert service.story_progress("mq_season_unending") == (0, 4)
    assert service.evaluate("mq_fallen_capture_odahviing").status is TaskStatus.LOCKED
    service.set_task_state("mq_season_negotiate", TaskStatus.COMPLETE)
    assert service.evaluate("mq_fallen_capture_odahviing").status is TaskStatus.AVAILABLE


def test_truce_bypass_excludes_conditional_story_and_unlocks_capture(service):
    service.set_task_state("mq_fallen_plan_esbern", TaskStatus.COMPLETE, confirm_choice=True)
    service.set_task_state(
        "mq_fallen_ask_jarl", TaskStatus.COMPLETE, outcome_id="truce_bypassed"
    )
    assert service.story_progress("mq_season_unending") == (0, 0)
    assert service.evaluate("mq_season_negotiate").status is TaskStatus.NOT_APPLICABLE
    assert service.evaluate("mq_fallen_capture_odahviing").status is TaskStatus.AVAILABLE


def test_associated_tasks_do_not_block_story_completion(service):
    required = {
        membership.task_id
        for membership in service.content.memberships.values()
        if membership.story_id == "mq_world_eater_eyrie"
        and membership.completion_role is CompletionRole.REQUIRED
    }
    for task_id in required:
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    assert service.story_progress("mq_world_eater_eyrie")[0] == service.story_progress(
        "mq_world_eater_eyrie"
    )[1]
    assert service.state.get_task_state("mask_nahkriin") is None
    assert service.state.get_task_state("shout_storm_call_skuldafn") is None


def test_expiration_preserves_underlying_state_and_excludes_denominator(service):
    service.set_task_state("mq_skuldafn_defeat_nahkriin", TaskStatus.COMPLETE)
    service.set_task_state("mask_nahkriin", TaskStatus.DEFERRED)
    before = service.story_progress("mask_skuldafn")
    assert before == (0, 1)
    service.set_task_state("mq_skuldafn_enter_sovngarde", TaskStatus.COMPLETE)
    expired = service.evaluate("mask_nahkriin")
    assert expired.status is TaskStatus.NOT_APPLICABLE
    assert expired.stored_state is TaskStatus.DEFERRED
    assert service.story_progress("mask_skuldafn") == (0, 0)
    service.set_task_state("mq_skuldafn_enter_sovngarde", None)
    assert service.evaluate("mask_nahkriin").status is TaskStatus.DEFERRED


def test_spared_resolution_is_reversible_and_kill_requires_confirmation(service):
    service.set_manual_choice("paarthurnax_resolution", "spared")
    assert service.evaluate("mq_paarthurnax_kill").status is TaskStatus.NOT_APPLICABLE
    assert service.evaluate("mq_paarthurnax_report").status is TaskStatus.NOT_APPLICABLE
    with pytest.raises(ChoiceConfirmationRequired):
        service.set_task_state("mq_paarthurnax_kill", TaskStatus.COMPLETE)
    service.set_task_state("mq_paarthurnax_kill", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.state.get_choice("paarthurnax_resolution") == "killed"
    service.set_task_state("mq_paarthurnax_kill", None)
    assert service.state.get_choice("paarthurnax_resolution") is None


def test_special_destinations_gate_in_order_and_surface_missables(service):
    initial = service.operational_regions()
    assert "skuldafn" not in {region.id for region in initial[RegionType.SPECIAL_DESTINATION]}
    assert "sovngarde" not in {region.id for region in initial[RegionType.SPECIAL_DESTINATION]}
    service.set_task_state("mq_world_eater_depart_skuldafn", TaskStatus.COMPLETE)
    special = service.operational_regions()[RegionType.SPECIAL_DESTINATION]
    assert "skuldafn" in {region.id for region in special}
    skuldafn = next(item for item in service.regional_plan("skuldafn") if item.id == "skuldafn")
    assert {"claw_diamond_skuldafn", "shout_storm_call_skuldafn"} <= {
        item.task.id for item in skuldafn.tasks
    }
    assert skuldafn.warning_text
    assert "mq_sovngarde_hall" not in regional_task_ids(service, "sovngarde")
    service.set_task_state("mq_skuldafn_enter_sovngarde", TaskStatus.COMPLETE)
    assert "mq_sovngarde_hall" in regional_task_ids(service, "sovngarde")


def test_required_main_quest_can_fully_complete_without_optional_or_bypassed_tasks(service):
    service.set_task_state("mq_fallen_plan_arngeir", TaskStatus.COMPLETE, confirm_choice=True)
    service.set_task_state(
        "mq_fallen_ask_jarl", TaskStatus.COMPLETE, outcome_id="truce_bypassed"
    )
    for task_id in main_required_task_ids(service):
        if task_id not in {"mq_fallen_plan_paarthurnax", "mq_fallen_plan_esbern"}:
            if task_id == "mq_fallen_ask_jarl":
                continue
            service.set_task_state(task_id, TaskStatus.COMPLETE, confirm_choice=True)
    completed, total = service.collection_progress("skyrim_main_quest")
    assert completed == total
    assert service.state.get_task_state("mq_paarthurnax_kill") is None
    assert service.evaluate("mq_season_negotiate").status is TaskStatus.NOT_APPLICABLE


def test_main_quest_audit_matches_canonical_graph():
    root = Path(loader_module.__file__).parents[3]
    audit = (root / "docs" / "main-quest-task-audit.md").read_text(encoding="utf-8")
    assert audit == render_audit()
