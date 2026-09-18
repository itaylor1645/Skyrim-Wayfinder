from __future__ import annotations

from pathlib import Path

import json
import shutil

import pytest

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_masks_claws_audit import REUSED, render_audit
from skyrim_wayfinder.domain import TaskStatus
from skyrim_wayfinder.data import CanonicalDataError, load_canonical_content


def test_approved_collectible_scope_and_reuse(content):
    masks = [item for item in content.collectibles.values() if item.collection_id == "dragon_priest_masks"]
    claws = [item for item in content.collectibles.values() if item.collection_id == "dragon_claws"]
    assert len(masks) == 14
    assert len(claws) == 11
    assert len(content.collectible_credits) == 27
    assert len({item.task_id for item in content.collectible_credits.values()}) == 27
    assert REUSED <= {item.task_id for item in content.collectible_credits.values()}


def test_collection_progress_counts_identities_not_acquisition_tasks(service):
    assert service.collection_progress("dragon_claws") == (0, 11)
    service.set_task_state("claw_amethyst_left_vahloks_tomb", TaskStatus.COMPLETE)
    assert service.collection_progress("dragon_claws") == (0, 11)
    service.set_task_state("claw_amethyst_right_vahloks_tomb", TaskStatus.COMPLETE)
    assert service.collection_progress("dragon_claws") == (1, 11)


def test_coral_alternative_is_derived_and_reversible(service):
    first = "claw_coral_buy_winterhold"
    alternate = "claw_coral_yngol_barrow"
    service.set_task_state(first, TaskStatus.COMPLETE)
    assert service.collectible_progress("dragon_claw_coral") == (1, 1)
    assert service.evaluate(alternate).status is TaskStatus.NOT_APPLICABLE
    assert service.state.get_task_state(alternate) is None
    service.set_task_state(first, None)
    assert service.evaluate(alternate).status is TaskStatus.AVAILABLE


def test_amethyst_requires_two_distinct_task_sources(service):
    left = "claw_amethyst_left_vahloks_tomb"
    right = "claw_amethyst_right_vahloks_tomb"
    service.set_access_condition("access_vahloks_tomb", True)
    service.set_task_state(left, TaskStatus.COMPLETE)
    assert service.collectible_progress("dragon_claw_amethyst") == (1, 2)
    assert service.story_progress("claw_amethyst") == (0, 1)
    service.set_task_state(right, TaskStatus.COMPLETE)
    assert service.collectible_progress("dragon_claw_amethyst") == (2, 2)
    assert service.story_progress("claw_amethyst") == (1, 1)


def test_konahrik_preparation_tracks_current_possession_without_undoing_history(service):
    prep = "prep_konahrik_masks"
    konahrik = "mask_konahrik"
    assert service.evaluate(prep).status is TaskStatus.LOCKED
    assert prep not in {item.task.id for item in service.outstanding_preparations()}
    required = service.content.tasks[prep].required_collectible_ids
    for collectible_id in required:
        credit = next(
            item for item in service.content.collectible_credits.values()
            if item.collectible_id == collectible_id
        )
        service.set_task_state(credit.task_id, TaskStatus.COMPLETE)
    assert service.evaluate(prep).status is TaskStatus.ACTIVE
    assert prep in {item.task.id for item in service.outstanding_preparations()}
    assert service.evaluate(konahrik).status is TaskStatus.LOCKED
    service.set_task_state(prep, TaskStatus.COMPLETE)
    assert service.evaluate(konahrik).status is TaskStatus.AVAILABLE
    service.set_task_state(konahrik, TaskStatus.COMPLETE)
    service.set_task_state(prep, None)
    assert service.evaluate(konahrik).status is TaskStatus.COMPLETE
    assert prep not in {item.task.id for item in service.outstanding_preparations()}


def test_sapphire_claw_replaces_temporary_shroud_hearth_bridge(service):
    task = service.content.tasks["shout_kynes_peace_shroud_hearth_barrow"]
    assert "access_shroud_hearth_depths" not in service.content.access_conditions
    assert not task.access_condition_ids
    assert [item.task_id for item in task.prerequisites] == ["claw_sapphire_ivarstead"]
    assert service.evaluate(task.id).status is TaskStatus.LOCKED
    service.set_task_state("claw_sapphire_ivarstead", TaskStatus.COMPLETE)
    assert service.evaluate(task.id).status is TaskStatus.AVAILABLE


def test_missable_and_one_way_semantics_are_narrow(content):
    assert content.tasks["mask_nahkriin"].missable
    assert content.tasks["mask_nahkriin"].one_way
    assert content.tasks["mask_miraak"].missable
    assert not content.tasks["mask_miraak"].one_way
    assert content.tasks["mask_miraak"].expires_after_task_id is None
    assert content.tasks["mask_miraak"].access_condition_ids == ("access_waking_dreams",)


def test_masks_claws_audit_matches_canonical_data():
    root = Path(loader_module.__file__).parents[3]
    assert (root / "docs" / "masks-claws-task-audit.md").read_text(encoding="utf-8") == render_audit()


def test_duplicate_collectible_task_source_is_rejected(tmp_path):
    source = Path(loader_module.__file__).parent / "canonical"
    target = tmp_path / "canonical"
    shutil.copytree(source, target)
    path = target / "collectible_credits.json"
    credits = json.loads(path.read_text(encoding="utf-8"))
    duplicate = dict(credits[0])
    duplicate["id"] = "duplicate_credit_id"
    credits.append(duplicate)
    path.write_text(json.dumps(credits, indent=2), encoding="utf-8")
    with pytest.raises(CanonicalDataError, match="Duplicate collectible task source"):
        load_canonical_content(target)


def test_collectible_collection_and_story_references_are_validated(tmp_path):
    source = Path(loader_module.__file__).parent / "canonical"
    target = tmp_path / "canonical"
    shutil.copytree(source, target)
    path = target / "collectibles.json"
    collectibles = json.loads(path.read_text(encoding="utf-8"))
    collectibles[0]["story_id"] = "missing_story"
    path.write_text(json.dumps(collectibles, indent=2), encoding="utf-8")
    with pytest.raises(CanonicalDataError, match="unknown story"):
        load_canonical_content(target)
