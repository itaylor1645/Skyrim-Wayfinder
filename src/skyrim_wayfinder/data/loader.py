from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from skyrim_wayfinder.domain import (
    AccessCondition,
    CanonicalContent,
    Choice,
    ChoiceOption,
    Collection,
    CollectibleCompletionRule,
    CollectibleCredit,
    CollectibleDefinition,
    CompletionRole,
    CompletionDomain,
    ContentSource,
    GeographyType,
    Location,
    LocationType,
    PlannerBehavior,
    Prerequisite,
    RegionType,
    Story,
    StoryClassification,
    ShoutCredit,
    ShoutDefinition,
    Task,
    TaskMembership,
    TravelRegion,
    VerificationStatus,
)


class CanonicalDataError(ValueError):
    pass


FILES = (
    "completion_domains.json", "collections.json", "stories.json",
    "task_memberships.json", "regions.json", "locations.json", "choices.json",
    "tasks.json", "access_conditions.json", "shouts.json", "shout_credits.json",
    "collectibles.json", "collectible_credits.json", "theme.json",
)


def _directory() -> Path:
    return Path(__file__).parent / "canonical"


def _read(directory: Path, name: str) -> Any:
    path = directory / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonicalDataError(f"Unable to load {path}: {exc}") from exc


def _unique_by_id(items: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise CanonicalDataError(f"{label} contains an invalid or missing ID")
        if not re.fullmatch(r"[a-z0-9_]+", identifier):
            raise CanonicalDataError(f"{label} has non-canonical ID: {identifier}")
        if identifier in result:
            raise CanonicalDataError(f"Duplicate {label} ID: {identifier}")
        result[identifier] = item
    return result


def _reject_geography(items: list[dict[str, Any]], label: str) -> None:
    forbidden = {"region_id", "travel_region_id", "location_id"}
    for item in items:
        found = forbidden.intersection(item)
        if found:
            raise CanonicalDataError(
                f"{label} {item.get('id', '<unknown>')} may not contain geography: {sorted(found)}"
            )


def load_canonical_content(directory: str | Path | None = None) -> CanonicalContent:
    root = Path(directory) if directory else _directory()
    raw = {name: _read(root, name) for name in FILES}

    for name in FILES[:-1]:
        if not isinstance(raw[name], list):
            raise CanonicalDataError(f"{name} must contain a JSON list")
    id_labels = {
        "completion_domains.json": "domain",
        "collections.json": "collection",
        "stories.json": "story",
        "regions.json": "region",
        "locations.json": "location",
        "task_memberships.json": "membership",
        "choices.json": "choice",
        "tasks.json": "task",
        "access_conditions.json": "access condition",
        "shouts.json": "shout",
        "shout_credits.json": "shout credit",
        "collectibles.json": "collectible",
        "collectible_credits.json": "collectible credit",
    }
    for name in (
        "completion_domains.json", "collections.json", "stories.json", "regions.json",
        "locations.json", "task_memberships.json", "choices.json", "tasks.json",
        "access_conditions.json", "shouts.json", "shout_credits.json",
        "collectibles.json", "collectible_credits.json",
    ):
        _unique_by_id(raw[name], id_labels[name])
    _reject_geography(raw["completion_domains.json"], "Domain")
    _reject_geography(raw["collections.json"], "Collection")
    _reject_geography(raw["stories.json"], "Story")
    _reject_geography(raw["task_memberships.json"], "Membership")

    domains = {
        item["id"]: CompletionDomain(**item)
        for item in raw["completion_domains.json"]
    }
    collections = {
        item["id"]: Collection(**item) for item in raw["collections.json"]
    }
    stories = {}
    for item in raw["stories.json"]:
        prepared = dict(item)
        prepared["classification"] = StoryClassification(prepared.get("classification", "REQUIRED"))
        stories[prepared["id"]] = Story(**prepared)

    regions: dict[str, TravelRegion] = {}
    for item in raw["regions.json"]:
        prepared = dict(item)
        prepared["region_type"] = RegionType(prepared["region_type"])
        region = TravelRegion(**prepared)
        if region.id in regions:
            raise CanonicalDataError(f"Duplicate region ID: {region.id}")
        regions[region.id] = region

    locations: dict[str, Location] = {}
    for item in raw["locations.json"]:
        prepared = dict(item)
        prepared["aliases"] = tuple(prepared.get("aliases", ()))
        prepared["source_urls"] = tuple(prepared.get("source_urls", ()))
        prepared["location_type"] = LocationType(prepared["location_type"])
        prepared["content_source"] = ContentSource(prepared["content_source"])
        prepared["verification_status"] = VerificationStatus(prepared["verification_status"])
        location = Location(**prepared)
        if location.id in locations:
            raise CanonicalDataError(f"Duplicate location ID: {location.id}")
        locations[location.id] = location

    choices: dict[str, Choice] = {}
    for item in raw["choices.json"]:
        if item["id"] in choices:
            raise CanonicalDataError(f"Duplicate choice ID: {item['id']}")
        options = {
            option["id"]: ChoiceOption(
                id=option["id"], label=option["label"],
                excludes_options=tuple(option.get("excludes_options", ())),
                manual_resolution=option.get("manual_resolution", False),
            )
            for option in item["options"]
        }
        choices[item["id"]] = Choice(
            id=item["id"], title=item["title"], options=options,
            source_url=item.get("source_url"),
        )

    tasks: dict[str, Task] = {}
    for item in raw["tasks.json"]:
        forbidden = {"region_id", "travel_region_id", "visit_id", "epic_id", "story_id", "additional_categories"}
        found = forbidden.intersection(item)
        if found:
            raise CanonicalDataError(f"Task {item['id']} contains retired fields: {sorted(found)}")
        prepared = dict(item)
        prepared["geography_type"] = GeographyType(prepared["geography_type"])
        prepared["planner_behavior"] = PlannerBehavior(prepared["planner_behavior"])
        prepared["preparation_for"] = tuple(prepared.get("preparation_for", ()))
        prepared["any_of_task_ids"] = tuple(prepared.get("any_of_task_ids", ()))
        prepared["access_condition_ids"] = tuple(prepared.get("access_condition_ids", ()))
        prepared["required_collectible_ids"] = tuple(prepared.get("required_collectible_ids", ()))
        prepared["prerequisites"] = tuple(
            Prerequisite(**condition) for condition in prepared.get("prerequisites", ())
        )
        task = Task(**prepared)
        tasks[task.id] = task

    memberships: dict[str, TaskMembership] = {}
    for item in raw["task_memberships.json"]:
        prepared = dict(item)
        if "completion_role" not in prepared:
            raise CanonicalDataError(f"Membership {prepared['id']} has no explicit completion_role")
        prepared["completion_role"] = CompletionRole(prepared["completion_role"])
        membership = TaskMembership(**prepared)
        if membership.id in memberships:
            raise CanonicalDataError(f"Duplicate membership ID: {membership.id}")
        memberships[membership.id] = membership

    access_conditions = {}
    for item in raw["access_conditions.json"]:
        prepared = dict(item)
        prepared["source_urls"] = tuple(prepared.get("source_urls", ()))
        prepared["content_source"] = ContentSource(prepared["content_source"])
        access_conditions[prepared["id"]] = AccessCondition(**prepared)
    shouts = {}
    for item in raw["shouts.json"]:
        prepared = dict(item)
        prepared["words"] = tuple(prepared["words"])
        prepared["content_source"] = ContentSource(prepared["content_source"])
        shouts[prepared["id"]] = ShoutDefinition(**prepared)
    shout_credits = {item["id"]: ShoutCredit(**item) for item in raw["shout_credits.json"]}
    collectibles = {}
    for item in raw["collectibles.json"]:
        prepared = dict(item)
        prepared["completion_rule"] = CollectibleCompletionRule(prepared["completion_rule"])
        prepared["content_source"] = ContentSource(prepared["content_source"])
        collectibles[prepared["id"]] = CollectibleDefinition(**prepared)
    collectible_credits = {
        item["id"]: CollectibleCredit(**item) for item in raw["collectible_credits.json"]
    }

    fingerprint_payload = json.dumps(raw, sort_keys=True, separators=(",", ":"))
    content = CanonicalContent(
        domains=domains, collections=collections, stories=stories,
        memberships=memberships, regions=regions, locations=locations,
        tasks=tasks, choices=choices, access_conditions=access_conditions,
        shouts=shouts, shout_credits=shout_credits, collectibles=collectibles,
        collectible_credits=collectible_credits, theme=raw["theme.json"],
        fingerprint=hashlib.sha256(fingerprint_payload.encode()).hexdigest(),
    )
    _validate(content)
    return content


def _validate(content: CanonicalContent) -> None:
    errors: list[str] = []
    for collection in content.collections.values():
        if collection.domain_id not in content.domains:
            errors.append(f"Collection {collection.id} references unknown domain {collection.domain_id}")
    for story in content.stories.values():
        if story.collection_id not in content.collections:
            errors.append(f"Story {story.id} references unknown collection {story.collection_id}")
        if story.resolution_choice_id and story.resolution_choice_id not in content.choices:
            errors.append(
                f"Story {story.id} references unknown resolution choice {story.resolution_choice_id}"
            )
    for choice in content.choices.values():
        for option in choice.options.values():
            for excluded_option in option.excludes_options:
                if excluded_option not in choice.options:
                    errors.append(
                        f"Choice {choice.id} option {option.id} excludes unknown option {excluded_option}"
                    )
    for location in content.locations.values():
        if location.region_id not in content.regions:
            errors.append(f"Location {location.id} references unknown region {location.region_id}")
    for region in content.regions.values():
        if region.departure_location_id and region.departure_location_id not in content.locations:
            errors.append(
                f"Region {region.id} references unknown departure location {region.departure_location_id}"
            )

    aliases: dict[str, str] = {}
    for location in content.locations.values():
        for alias in (location.display_name, *location.aliases):
            normalized = " ".join(unicodedata.normalize("NFKC", alias).casefold().split())
            owner = aliases.get(normalized)
            if owner:
                if owner != location.id:
                    errors.append(f"Ambiguous location alias '{alias}' resolves to {owner} and {location.id}")
                else:
                    errors.append(f"Duplicate normalized alias '{alias}' on Location {location.id}")
            aliases[normalized] = location.id
        if not location.source_urls or any(not url.startswith("https://") for url in location.source_urls):
            errors.append(f"Location {location.id} must have at least one HTTPS source URL")
        if not location.assignment_rationale.strip():
            errors.append(f"Location {location.id} must have an assignment rationale")
        if (
            location.gated or location.one_way or location.missable or location.requires_special_access
        ) and not location.access_notes:
            errors.append(f"Location {location.id} access flags require access_notes")

    for task in content.tasks.values():
        if task.geography_type is GeographyType.PHYSICAL:
            if not task.location_id:
                errors.append(f"Physical task {task.id} has no location")
            elif task.location_id not in content.locations:
                errors.append(f"Task {task.id} references unknown location {task.location_id}")
        elif task.location_id is not None:
            errors.append(f"Locationless task {task.id} may not reference a location")
        if task.planner_behavior is PlannerBehavior.REGIONAL_ACTION and task.geography_type is not GeographyType.PHYSICAL:
            errors.append(f"Regional action {task.id} must be physical")
        if task.planner_behavior in {
            PlannerBehavior.GLOBAL_ACTION, PlannerBehavior.PREPARATION,
            PlannerBehavior.OPPORTUNISTIC, PlannerBehavior.MILESTONE,
        } and task.geography_type is not GeographyType.LOCATIONLESS:
            errors.append(f"{task.planner_behavior.value} task {task.id} must be locationless")
        if task.choice_id:
            choice = content.choices.get(task.choice_id)
            if not choice or task.choice_option not in choice.options:
                errors.append(f"Task {task.id} has invalid choice option")
        if task.sets_choice and (not task.choice_id or not task.choice_option):
            errors.append(f"Choice-setting task {task.id} has no choice option")
        if bool(task.applicable_outcome_task_id) != bool(task.applicable_outcome):
            errors.append(f"Task {task.id} has an incomplete applicable outcome condition")
        if task.applicable_outcome_task_id:
            source = content.tasks.get(task.applicable_outcome_task_id)
            if not source or task.applicable_outcome not in source.outcome_options:
                errors.append(f"Task {task.id} has invalid applicable outcome")
        if task.expires_after_task_id and task.expires_after_task_id not in content.tasks:
            errors.append(f"Task {task.id} expiration references {task.expires_after_task_id}")
        for alternative_id in task.any_of_task_ids:
            if alternative_id not in content.tasks:
                errors.append(f"Task {task.id} alternative prerequisite references {alternative_id}")
        for condition in task.prerequisites:
            if condition.type in {"task_complete", "preparation_complete"} and condition.task_id not in content.tasks:
                errors.append(f"Task {task.id} prerequisite references {condition.task_id}")
            if condition.when_outcome_task_id:
                source = content.tasks.get(condition.when_outcome_task_id)
                if not source or condition.when_outcome not in source.outcome_options:
                    errors.append(f"Task {task.id} prerequisite has invalid outcome condition")
            elif condition.when_outcome:
                errors.append(f"Task {task.id} prerequisite has an incomplete outcome condition")
        for target_id in task.preparation_for:
            if target_id not in content.tasks:
                errors.append(f"Preparation {task.id} references {target_id}")
        for condition_id in task.access_condition_ids:
            if condition_id not in content.access_conditions:
                errors.append(f"Task {task.id} references unknown access condition {condition_id}")
        for collectible_id in task.required_collectible_ids:
            if collectible_id not in content.collectibles:
                errors.append(f"Task {task.id} requires unknown collectible {collectible_id}")

    for shout in content.shouts.values():
        if shout.collection_id not in content.collections:
            errors.append(f"Shout {shout.id} references unknown collection {shout.collection_id}")
        if len(shout.words) != 3:
            errors.append(f"Shout {shout.id} must define exactly three ordered words")
    for credit in content.shout_credits.values():
        if credit.task_id not in content.tasks or credit.shout_id not in content.shouts:
            errors.append(f"Shout credit {credit.id} has an invalid reference")
        if credit.credit_count not in {1, 2, 3}:
            errors.append(f"Shout credit {credit.id} has invalid credit_count")

    collectible_task_pairs: set[tuple[str, str]] = set()
    for collectible in content.collectibles.values():
        if collectible.collection_id not in content.collections:
            errors.append(f"Collectible {collectible.id} references unknown collection")
        if collectible.story_id not in content.stories:
            errors.append(f"Collectible {collectible.id} references unknown story")
        elif content.stories[collectible.story_id].collection_id != collectible.collection_id:
            errors.append(f"Collectible {collectible.id} story is outside its collection")
        if collectible.required_credit_count < 1:
            errors.append(f"Collectible {collectible.id} requires no credits")
        if not collectible.source_url.startswith("https://"):
            errors.append(f"Collectible {collectible.id} requires an HTTPS source URL")
    for credit in content.collectible_credits.values():
        if credit.task_id not in content.tasks or credit.collectible_id not in content.collectibles:
            errors.append(f"Collectible credit {credit.id} has an invalid reference")
        if credit.credit_count < 1:
            errors.append(f"Collectible credit {credit.id} has invalid credit_count")
        pair = (credit.task_id, credit.collectible_id)
        if pair in collectible_task_pairs:
            errors.append(f"Duplicate collectible task source: {pair}")
        collectible_task_pairs.add(pair)

    dependency_graph = {
        task.id: {
            condition.task_id
            for condition in task.prerequisites
            if condition.type in {"task_complete", "preparation_complete"} and condition.task_id
        } | set(task.any_of_task_ids)
        for task in content.tasks.values()
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, path: tuple[str, ...]) -> None:
        if task_id in visiting:
            cycle_start = path.index(task_id) if task_id in path else 0
            errors.append(f"Prerequisite cycle: {' -> '.join((*path[cycle_start:], task_id))}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency_id in dependency_graph.get(task_id, ()):
            if dependency_id in content.tasks:
                visit(dependency_id, (*path, task_id))
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in content.tasks:
        visit(task_id, ())

    membership_pairs: set[tuple[str, str]] = set()
    primary_counts = {task_id: 0 for task_id in content.tasks}
    for membership in content.memberships.values():
        if membership.task_id not in content.tasks:
            errors.append(f"Membership {membership.id} references unknown task {membership.task_id}")
        if membership.story_id not in content.stories:
            errors.append(f"Membership {membership.id} references unknown story {membership.story_id}")
        pair = (membership.task_id, membership.story_id)
        if pair in membership_pairs:
            errors.append(f"Duplicate task/story membership: {pair}")
        membership_pairs.add(pair)
        if membership.is_primary and membership.task_id in primary_counts:
            primary_counts[membership.task_id] += 1
    for task_id, count in primary_counts.items():
        if count != 1:
            errors.append(f"Task {task_id} must have exactly one primary membership; found {count}")
    if errors:
        raise CanonicalDataError("; ".join(errors))
