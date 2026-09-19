from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import skyrim_wayfinder.data.loader as loader_module
from scripts.generate_geography_review import render_review
from skyrim_wayfinder.data import CanonicalDataError, load_canonical_content
from skyrim_wayfinder.domain import (
    ContentSource,
    GeographyType,
    LocationType,
    RegionType,
    VerificationStatus,
)


def copied_canonical(tmp_path: Path) -> Path:
    source = Path(loader_module.__file__).parent / "canonical"
    target = tmp_path / "canonical"
    shutil.copytree(source, target)
    return target


def read_json(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def write_json(root: Path, name: str, value) -> None:
    (root / name).write_text(json.dumps(value, indent=2), encoding="utf-8")


def test_every_physical_task_derives_one_valid_region_from_location(content):
    for task in content.tasks.values():
        assert not hasattr(task, "region_id")
        if task.geography_type is GeographyType.PHYSICAL:
            assert task.location_id in content.locations
            assert content.locations[task.location_id].region_id in content.regions
        else:
            assert task.location_id is None


def test_completion_taxonomy_has_no_geography(content):
    for item in (*content.domains.values(), *content.collections.values(), *content.stories.values()):
        assert not hasattr(item, "region_id")
        assert not hasattr(item, "location_id")


def test_duplicate_raw_location_ids_are_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    locations = read_json(root, "locations.json")
    locations.append(dict(locations[0]))
    write_json(root, "locations.json", locations)
    with pytest.raises(CanonicalDataError, match="Duplicate location ID"):
        load_canonical_content(root)


def test_duplicate_raw_region_ids_are_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    regions = read_json(root, "regions.json")
    regions.append(dict(regions[0]))
    write_json(root, "regions.json", regions)
    with pytest.raises(CanonicalDataError, match="Duplicate region ID"):
        load_canonical_content(root)


def test_ambiguous_location_aliases_are_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    locations = read_json(root, "locations.json")
    locations[0].setdefault("aliases", []).append("Shared Place")
    locations[1].setdefault("aliases", []).append(" shared   place ")
    write_json(root, "locations.json", locations)
    with pytest.raises(CanonicalDataError, match="Ambiguous location alias"):
        load_canonical_content(root)


def test_unicode_normalized_aliases_are_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    locations = read_json(root, "locations.json")
    locations[0].setdefault("aliases", []).append("Ｃｏｌｌｉｓｉｏｎ")
    locations[1].setdefault("aliases", []).append("collision")
    write_json(root, "locations.json", locations)
    with pytest.raises(CanonicalDataError, match="Ambiguous location alias"):
        load_canonical_content(root)


def test_story_geography_is_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    stories = read_json(root, "stories.json")
    stories[0]["region_id"] = "whiterun"
    write_json(root, "stories.json", stories)
    with pytest.raises(CanonicalDataError, match="may not contain geography"):
        load_canonical_content(root)


def test_membership_geography_is_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    memberships = read_json(root, "task_memberships.json")
    memberships[0]["location_id"] = "dragonsreach"
    write_json(root, "task_memberships.json", memberships)
    with pytest.raises(CanonicalDataError, match="Membership.*may not contain geography"):
        load_canonical_content(root)


def test_task_region_override_is_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    tasks = read_json(root, "tasks.json")
    tasks[0]["region_id"] = "whiterun"
    write_json(root, "tasks.json", tasks)
    with pytest.raises(CanonicalDataError, match="retired fields"):
        load_canonical_content(root)


def test_locationless_task_with_location_is_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    tasks = read_json(root, "tasks.json")
    milestone = next(item for item in tasks if item["id"] == "daedric_break_of_dawn_beacon")
    milestone["location_id"] = "dragonsreach"
    write_json(root, "tasks.json", tasks)
    with pytest.raises(CanonicalDataError, match="Locationless task"):
        load_canonical_content(root)


def test_exactly_one_primary_membership_is_required(tmp_path):
    root = copied_canonical(tmp_path)
    memberships = read_json(root, "task_memberships.json")
    for item in memberships:
        if item["task_id"] == "mask_morokei":
            item["is_primary"] = False
    write_json(root, "task_memberships.json", memberships)
    with pytest.raises(CanonicalDataError, match="exactly one primary membership"):
        load_canonical_content(root)


def test_every_membership_requires_explicit_completion_role(tmp_path):
    root = copied_canonical(tmp_path)
    memberships = read_json(root, "task_memberships.json")
    memberships[0].pop("completion_role")
    write_json(root, "task_memberships.json", memberships)
    with pytest.raises(CanonicalDataError, match="explicit completion_role"):
        load_canonical_content(root)


def test_prerequisite_cycles_are_rejected(tmp_path):
    root = copied_canonical(tmp_path)
    tasks = read_json(root, "tasks.json")
    by_id = {item["id"]: item for item in tasks}
    by_id["mq_unbound_escape_helgen"]["prerequisites"] = [
        {"type": "task_complete", "task_id": "mq_before_storm_go_whiterun"}
    ]
    write_json(root, "tasks.json", tasks)
    with pytest.raises(CanonicalDataError, match="Prerequisite cycle"):
        load_canonical_content(root)


def test_geography_foundation_metadata_is_complete(content):
    assert len(content.regions) == 21
    assert len(content.locations) == 248
    assert all(region.region_type in RegionType for region in content.regions.values())
    assert all(region.region_type is not getattr(RegionType, "GLOBAL", None) for region in content.regions.values())
    assert all(location.location_type in LocationType for location in content.locations.values())
    assert all(location.content_source in ContentSource for location in content.locations.values())
    assert all(location.source_urls for location in content.locations.values())
    assert all(location.assignment_rationale for location in content.locations.values())
    assert all(location.verification_status in VerificationStatus for location in content.locations.values())
    assert not any(hasattr(region, "representative_location_ids") for region in content.regions.values())


def test_accepted_location_assignments_remain_stable(content):
    expected = {
        "riverwood": "whiterun",
        "riverwood_trader": "whiterun",
        "dragonsreach": "whiterun",
        "bleak_falls_barrow": "whiterun",
        "western_watchtower": "whiterun",
        "fellglow_keep": "whiterun",
        "helgen_keep": "falkreath",
        "high_hrothgar": "high_hrothgar",
        "college_of_winterhold": "winterhold",
        "saarthal": "winterhold",
        "winterhold": "winterhold",
        "mzulft": "windhelm",
        "labyrinthian": "labyrinthian",
        "scorched_hammer": "riften",
        "honorhall_orphanage": "riften",
        "aretino_residence": "windhelm",
        "abandoned_shack": "morthal",
        "skuldafn": "skuldafn",
        "northwind_summit": "riften",
        "broken_tower_redoubt": "markarth",
        "brucas_leap_redoubt": "markarth",
        "druadach_redoubt": "markarth",
        "hag_rock_redoubt": "markarth",
        "red_eagle_redoubt": "markarth",
        "glacial_cave": "solstheim_north",
        "castle_karstaag_ruins": "solstheim_north",
    }
    assert {item: content.locations[item].region_id for item in expected} == expected


def test_coverage_and_review_artifacts_match_catalog(content):
    root = Path(loader_module.__file__).parents[3]
    coverage = json.loads((root / "docs" / "geography-coverage.json").read_text(encoding="utf-8"))
    covered = {
        location_id
        for domain in coverage["domains"]
        for location_id in domain["location_ids"]
    }
    assert covered == set(content.locations)
    review_ids = {
        location.id
        for location in content.locations.values()
        if location.verification_status is VerificationStatus.REVIEW_REQUIRED
    }
    assert set(coverage["review_assignments"]) == review_ids
    assert not review_ids
    report = (root / "docs" / "geography-catalog-review.md").read_text(encoding="utf-8")
    assert f"{len(content.regions)} Travel Regions" in report
    assert f"{len(content.locations)} Locations" in report
    assert all(f"`{location_id}`" in report for location_id in review_ids)
    assert report == render_review()


def test_access_flags_require_explanatory_notes(tmp_path):
    root = copied_canonical(tmp_path)
    locations = read_json(root, "locations.json")
    locations[0]["gated"] = True
    locations[0].pop("access_notes", None)
    write_json(root, "locations.json", locations)
    with pytest.raises(CanonicalDataError, match="access flags require access_notes"):
        load_canonical_content(root)
