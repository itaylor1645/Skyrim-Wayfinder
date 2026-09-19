from __future__ import annotations

from pathlib import Path

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_daedric_artifacts_audit import QUEST_STORIES, render_audit
from skyrim_wayfinder.domain import PlannerBehavior, TaskStatus


def test_daedric_scope_and_achievement_metadata(content):
    artifacts = [item for item in content.collectibles.values() if item.collection_id == "daedric_artifacts"]
    assert len(QUEST_STORIES) == 15
    assert len(artifacts) == 19
    assert sum(item.oblivion_walker_eligible is True for item in artifacts) == 17
    assert content.collectibles["daedric_rueful_axe"].oblivion_walker_eligible is False
    assert content.collectibles["daedric_skeleton_key"].oblivion_walker_eligible is False
    assert all(item.oblivion_walker_eligible is not None for item in artifacts)


def test_every_daedric_artifact_has_one_identity_and_resolved_credit(content):
    artifacts = [item for item in content.collectibles.values() if item.collection_id == "daedric_artifacts"]
    for artifact in artifacts:
        credits = [item for item in content.collectible_credits.values() if item.collectible_id == artifact.id]
        assert len(credits) == 1
        assert credits[0].task_id in content.tasks


def test_reward_choice_changes_achievable_not_catalog_and_is_reversible(service):
    assert service.collectible_collection_summary("daedric_artifacts") == (0, 19, 19)
    service.set_task_state("artifact_azuras_star_acquire", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.evaluate("artifact_black_star_acquire").status is TaskStatus.NOT_APPLICABLE
    assert service.collectible_collection_summary("daedric_artifacts") == (1, 18, 19)
    service.set_task_state("artifact_azuras_star_acquire", None)
    assert service.evaluate("artifact_black_star_acquire").status is TaskStatus.LOCKED
    assert service.collectible_collection_summary("daedric_artifacts") == (0, 19, 19)


def test_nonartifact_quest_resolution_removes_reward_only_from_achievable(service):
    service.set_task_state("daedric_pieces_spare_silus", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.evaluate("artifact_mehrunes_razor_acquire").status is TaskStatus.NOT_APPLICABLE
    assert service.collectible_progress("daedric_mehrunes_razor") == (0, 0)
    assert service.collectible_collection_summary("daedric_artifacts") == (0, 18, 19)


def test_historical_acquisition_survives_later_branch_correction(service):
    service.set_task_state("artifact_mehrunes_razor_acquire", TaskStatus.COMPLETE, confirm_choice=True)
    service.set_task_state("daedric_pieces_spare_silus", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.evaluate("artifact_mehrunes_razor_acquire").status is TaskStatus.NOT_APPLICABLE
    assert service.collectible_progress("daedric_mehrunes_razor") == (1, 1)


def test_cursed_tribe_completion_does_not_credit_volendrung(service):
    for task_id in (
        "daedric_cursed_defend_largashbur", "prep_cursed_tribe_ingredients",
        "daedric_cursed_complete_ritual", "daedric_cursed_defeat_giant",
        "daedric_cursed_place_hammer",
    ):
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    complete, required = service.story_progress("daedric_cursed_tribe")
    assert complete == required
    assert service.collectible_progress("daedric_volendrung") == (0, 1)
    service.set_task_state("artifact_volendrung_acquire", TaskStatus.COMPLETE)
    assert service.collectible_progress("daedric_volendrung") == (1, 1)


def test_actual_level_gates_and_opportunistic_triggers(service):
    assert service.evaluate("daedric_boethiah_reach_sacellum").status is TaskStatus.LOCKED
    service.state.player_level = 30
    assert service.evaluate("daedric_boethiah_reach_sacellum").status is TaskStatus.AVAILABLE
    for task_id in ("daedric_break_of_dawn_beacon", "daedric_night_meet_sam", "daedric_ill_met_hunt_stag", "daedric_discerning_harvest_blood"):
        assert service.content.tasks[task_id].planner_behavior is PlannerBehavior.OPPORTUNISTIC
        assert all(
            task_id != evaluation.task.id
            for region in service.content.regions
            for card in service.regional_plan(region)
            for evaluation in card.tasks
        )


def test_observed_logrolf_destination_activates_exactly_one_location(service):
    milestone = "daedric_house_record_logrolf_location"
    variants = [task for task in service.content.tasks.values() if task.id.startswith("daedric_house_free_logrolf_")]
    assert len(variants) == 6
    assert all(service.evaluate(task.id).status is TaskStatus.NOT_APPLICABLE for task in variants)
    service.set_task_state(milestone, TaskStatus.COMPLETE, outcome_id="deepwood")
    applicable = [task for task in variants if service.evaluate(task.id).status is not TaskStatus.NOT_APPLICABLE]
    assert [task.id for task in applicable] == ["daedric_house_free_logrolf_deepwood"]
    service.set_task_state(milestone, None)
    service.set_task_state(milestone, TaskStatus.COMPLETE, outcome_id="red_eagle")
    applicable = [task for task in variants if service.evaluate(task.id).status is not TaskStatus.NOT_APPLICABLE]
    assert [task.id for task in applicable] == ["daedric_house_free_logrolf_red_eagle"]


def test_killing_captive_logrolf_removes_mace_from_achievable(service):
    service.set_task_state("daedric_house_record_logrolf_location", TaskStatus.COMPLETE, outcome_id="deepwood")
    service.set_task_state("daedric_house_kill_logrolf_deepwood", TaskStatus.COMPLETE, confirm_choice=True)
    assert service.evaluate("artifact_mace_molag_bal_acquire").status is TaskStatus.NOT_APPLICABLE
    assert service.collectible_progress("daedric_mace_molag_bal") == (0, 0)


def test_shared_elder_knowledge_route_works_in_both_orders(service):
    shared = "mq_elder_consult_septimus"
    assert service.evaluate(shared).status is TaskStatus.LOCKED
    service.set_task_state("daedric_discerning_seek_septimus", TaskStatus.COMPLETE)
    assert service.evaluate(shared).status is TaskStatus.AVAILABLE
    service.set_task_state("daedric_discerning_seek_septimus", None)
    service.set_task_state("mq_throat_meet_paarthurnax", TaskStatus.COMPLETE)
    assert service.evaluate(shared).status is TaskStatus.AVAILABLE
    memberships = {item.story_id for item in service.memberships_for_task(shared)}
    assert {"mq_elder_knowledge", "daedric_discerning"} <= memberships


def test_same_location_objectives_aggregate_without_task_reuse(service):
    service.state.player_level = 20
    service.set_task_state("daedric_pieces_visit_museum", TaskStatus.COMPLETE)
    cards = {card.location.id: card for card in service.regional_plan("markarth")}
    ids = {item.task.id for item in cards["dead_crone_rock"].tasks}
    assert {"daedric_pieces_recover_pommel", "shout_dismay_dead_crone_rock"} <= ids


def test_skeleton_key_bridge_is_narrow_and_permanent(service):
    task = service.content.tasks["artifact_skeleton_key_acquire"]
    assert task.location_id == "irkngthand"
    assert task.access_condition_ids == ("access_blindsighted_irkngthand",)
    service.set_task_state(task.id, TaskStatus.COMPLETE)
    assert service.collectible_progress("daedric_skeleton_key") == (1, 1)


def test_night_to_remember_optional_ring_route_is_truthful(service):
    task_id = "daedric_night_speak_ysolda"
    service.set_task_state(task_id, TaskStatus.COMPLETE, outcome_id="resolved")
    assert service.evaluate("daedric_night_retrieve_ring").status is TaskStatus.NOT_APPLICABLE
    service.set_task_state(task_id, None)
    service.set_task_state(task_id, TaskStatus.COMPLETE, outcome_id="retrieve_ring")
    assert service.evaluate("daedric_night_retrieve_ring").status is TaskStatus.AVAILABLE


def test_daedric_audit_matches_canonical_data():
    root = Path(loader_module.__file__).parents[3]
    assert (root / "docs" / "daedric-artifacts-task-audit.md").read_text(encoding="utf-8") == render_audit()
