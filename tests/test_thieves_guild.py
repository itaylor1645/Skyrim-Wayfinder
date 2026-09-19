from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_thieves_guild_audit import render_audit
from skyrim_wayfinder.domain import CompletionRole, StoryClassification, TaskStatus
from skyrim_wayfinder.persistence import StateRepository
from skyrim_wayfinder.services import TaskOutcomeRequired, WayfinderService


def plan_ids(service, region):
    return {evaluation.task.id for card in service.regional_plan(region) for evaluation in card.tasks}


def finish(service, *ids):
    for task_id in ids:
        outcomes = service.content.tasks[task_id].outcome_options
        service.set_task_state(
            task_id, TaskStatus.COMPLETE,
            outcome_id=next(iter(outcomes)) if outcomes else None,
        )


def guild_required_ids(service):
    return {
        membership.task_id
        for membership in service.content.memberships.values()
        if service.content.stories[membership.story_id].collection_id == "thieves_guild"
        and service.content.stories[membership.story_id].classification is StoryClassification.REQUIRED
        and membership.completion_role is CompletionRole.REQUIRED
    }


def test_scope_and_required_denominator(content):
    stories = [item for item in content.stories.values() if item.collection_id == "thieves_guild"]
    assert Counter(item.classification for item in stories) == {
        StoryClassification.REQUIRED: 16, StoryClassification.OPTIONAL: 5
    }
    assert "guild_paid_in_full" not in content.stories
    assert len(content.finite_progress) == 4
    assert all(item.required_count == 5 for item in content.finite_progress.values())


@pytest.mark.parametrize("outcome", ["success", "failed"])
def test_brynjolf_success_and_failure_both_continue(service, outcome):
    with pytest.raises(TaskOutcomeRequired):
        service.set_task_state("guild_chance_attempt", TaskStatus.COMPLETE)
    service.set_task_state("guild_chance_attempt", TaskStatus.COMPLETE, outcome_id=outcome)
    finish(service, "guild_chance_report")
    assert service.evaluate("guild_business_accept").status is TaskStatus.AVAILABLE
    assert service.story_progress("guild_chance_arrangement") == (2, 3)


def test_later_narrative_does_not_surface_early(service):
    assert service.evaluate("guild_snow_meet_mercer").status is TaskStatus.LOCKED
    assert service.evaluate("guild_blind_enter").status is TaskStatus.LOCKED
    assert service.evaluate("guild_dark_enter").status is TaskStatus.LOCKED
    assert "guild_blind_enter" not in plan_ids(service, "dawnstar")


def test_snow_access_binds_without_replacing_word_wall(service):
    word = service.content.tasks["shout_disarm_snow_veil_sanctum"]
    assert word.location_id == "snow_veil_sanctum"
    assert service.evaluate(word.id).status is TaskStatus.LOCKED
    finish(service, "guild_snow_open")
    assert service.is_access_condition_satisfied("access_snow_veil_sanctum")
    assert not service.state.is_access_condition_satisfied("access_snow_veil_sanctum")
    card = next(card for card in service.regional_plan("windhelm") if card.id == "snow_veil_sanctum")
    assert {"guild_snow_karliah", "guild_litany_ship", word.id} <= {item.task.id for item in card.tasks}
    memberships = [m for m in service.content.memberships.values() if m.task_id == word.id and m.story_id == "guild_speaking_silence"]
    assert len(memberships) == 1 and memberships[0].completion_role is CompletionRole.ASSOCIATED
    assert service.story_progress("guild_speaking_silence")[1] == 3


def test_irkngthand_key_and_eye_are_distinct(service):
    assert service.content.tasks["artifact_skeleton_key_acquire"].location_id == "irkngthand"
    finish(service, "guild_blind_enter")
    assert service.is_access_condition_satisfied("access_blindsighted_irkngthand")
    assert service.evaluate("artifact_skeleton_key_acquire").status is TaskStatus.LOCKED
    finish(service, "guild_blind_mercer")
    card = next(card for card in service.regional_plan("dawnstar") if card.id == "irkngthand")
    assert {"artifact_skeleton_key_acquire", "guild_litany_eye"} <= {item.task.id for item in card.tasks}
    finish(service, "artifact_skeleton_key_acquire")
    assert service.collectible_progress("daedric_skeleton_key") == (1, 1)
    finish(service, "guild_dark_return_key")
    assert service.collectible_progress("daedric_skeleton_key") == (1, 1)
    assert service.state.get_task_state("artifact_skeleton_key_acquire") is TaskStatus.COMPLETE
    assert service.story_progress("guild_blindsighted")[1] == 4


@pytest.mark.parametrize("city,story", [
    ("markarth", "guild_silver_lining"), ("solitude", "guild_dainty_sload"),
    ("whiterun", "guild_imitation_amnesty"), ("windhelm", "guild_summerset_shadows"),
])
def test_city_counter_unlocks_only_its_own_special_job(service, city, story):
    progress_id = f"guild_influence_{city}"
    accept_id = {
        "markarth": "guild_silver_accept", "solitude": "guild_sload_accept",
        "whiterun": "guild_amnesty_accept", "windhelm": "guild_shadows_accept"
    }[city]
    finish(service, "guild_business_report")
    service.set_finite_progress(progress_id, 4)
    assert service.evaluate(accept_id).status is TaskStatus.LOCKED
    service.set_finite_progress(progress_id, 5)
    assert service.evaluate(accept_id).status is TaskStatus.AVAILABLE
    assert all(service.evaluate(other).status is TaskStatus.LOCKED for other in (
        "guild_silver_accept", "guild_sload_accept", "guild_amnesty_accept", "guild_shadows_accept"
    ) if other != accept_id)
    service.set_finite_progress(progress_id, 8)
    assert service.finite_progress(progress_id) == (5, 5)
    service.set_finite_progress(progress_id, -2)
    assert service.finite_progress(progress_id) == (0, 5)
    assert service.evaluate(accept_id).status is TaskStatus.LOCKED
    finish(service, accept_id)
    assert service.evaluate(accept_id).status is TaskStatus.COMPLETE


def test_finite_progress_persists_and_does_not_create_tasks(content, tmp_path):
    path = tmp_path / "guild.sqlite3"
    repository = StateRepository(path)
    service = WayfinderService(content, repository)
    service.set_finite_progress("guild_influence_whiterun", 3)
    repository.close()
    reopened = StateRepository(path)
    assert reopened.get_finite_progress("guild_influence_whiterun") == 3
    assert "guild_influence_whiterun" not in content.tasks
    reopened.close()


def test_restoration_convergence_and_optional_nonblocking(service):
    finish(service, *guild_required_ids(service) - {"guild_management_ceremony", "guild_management_rewards"})
    assert service.thieves_guild_landmarks() == (True, False)
    assert service.evaluate("guild_management_ceremony").status is TaskStatus.AVAILABLE
    finish(service, "guild_management_ceremony", "guild_management_rewards")
    assert service.thieves_guild_landmarks() == (True, True)
    done, total = service.collection_progress("thieves_guild")
    assert done == total
    assert service.state.get_task_state("guild_litany_eye") is None
    assert service.state.get_task_state("guild_toying_journals") is None


def test_four_special_jobs_without_darkness_do_not_complete_guild(service):
    finish(service, "guild_silver_return", "guild_sload_return", "guild_amnesty_return", "guild_shadows_return")
    assert service.thieves_guild_landmarks() == (False, False)
    assert service.evaluate("guild_management_ceremony").status is TaskStatus.LOCKED


def test_radiant_jobs_and_random_places_are_not_canonical(content):
    forbidden = ("numbers_job", "fishing_job", "bedlam_job", "burglary_job", "shill_job", "sweep_job", "heist_job")
    assert not any(fragment in task_id for task_id in content.tasks for fragment in forbidden)
    assert len(content.locations) == 248
    assert content.locations["the_red_wave"].region_id == "solitude"
    assert content.locations["lake_honrich_quill_wreck"].region_id == "riften"


def test_vald_debt_obsolescence_is_nondestructive(service):
    finish(service, "guild_pursuit_plans")
    assert service.evaluate("guild_vald_maven").status is TaskStatus.NOT_APPLICABLE
    finish(service, "guild_vald_maven")
    assert service.evaluate("guild_vald_maven").status is TaskStatus.COMPLETE


def test_audit_matches_graph():
    root = Path(loader_module.__file__).parents[3]
    assert (root / "docs/thieves-guild-task-audit.md").read_text(encoding="utf-8") == render_audit()
