from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class TaskStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"
    LOCKED = "LOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RegionType(StrEnum):
    CITY = "CITY"
    EXPEDITION = "EXPEDITION"
    SPECIAL_DESTINATION = "SPECIAL_DESTINATION"


class LocationType(StrEnum):
    SETTLEMENT = "SETTLEMENT"
    BUILDING = "BUILDING"
    DUNGEON = "DUNGEON"
    EXTERIOR_SITE = "EXTERIOR_SITE"
    WORLDSPACE = "WORLDSPACE"


class ContentSource(StrEnum):
    SKYRIM = "SKYRIM"
    DAWNGUARD = "DAWNGUARD"
    HEARTHFIRE = "HEARTHFIRE"
    DRAGONBORN = "DRAGONBORN"


class VerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class GeographyType(StrEnum):
    PHYSICAL = "PHYSICAL"
    LOCATIONLESS = "LOCATIONLESS"


class PlannerBehavior(StrEnum):
    REGIONAL_ACTION = "REGIONAL_ACTION"
    GLOBAL_ACTION = "GLOBAL_ACTION"
    PREPARATION = "PREPARATION"
    OPPORTUNISTIC = "OPPORTUNISTIC"
    MILESTONE = "MILESTONE"


class StoryClassification(StrEnum):
    REQUIRED = "REQUIRED"
    CONDITIONAL = "CONDITIONAL"
    OPTIONAL = "OPTIONAL"


class CompletionRole(StrEnum):
    REQUIRED = "REQUIRED"
    ASSOCIATED = "ASSOCIATED"


class CollectibleCompletionRule(StrEnum):
    ANY = "ANY"
    ALL = "ALL"


@dataclass(frozen=True)
class CompletionDomain:
    id: str
    display_name: str
    description: str
    sort_order: int
    theme_key: str


@dataclass(frozen=True)
class Collection:
    id: str
    domain_id: str
    display_name: str
    description: str = ""
    sort_order: int = 0
    source_url: str | None = None


@dataclass(frozen=True)
class Story:
    id: str
    collection_id: str
    display_name: str
    description: str = ""
    sort_order: int = 0
    source_url: str | None = None
    classification: StoryClassification = StoryClassification.REQUIRED
    resolution_choice_id: str | None = None


@dataclass(frozen=True)
class TaskMembership:
    id: str
    task_id: str
    story_id: str
    is_primary: bool
    completion_role: CompletionRole
    sort_order: int = 0
    review_note: str | None = None


@dataclass(frozen=True)
class AccessCondition:
    id: str
    label: str
    description: str
    source_urls: tuple[str, ...]
    content_source: ContentSource


@dataclass(frozen=True)
class ShoutDefinition:
    id: str
    collection_id: str
    display_name: str
    words: tuple[str, ...]
    content_source: ContentSource
    source_url: str


@dataclass(frozen=True)
class ShoutCredit:
    id: str
    task_id: str
    shout_id: str
    credit_count: int


@dataclass(frozen=True)
class CollectibleDefinition:
    id: str
    collection_id: str
    story_id: str
    display_name: str
    required_credit_count: int
    completion_rule: CollectibleCompletionRule
    content_source: ContentSource
    source_url: str


@dataclass(frozen=True)
class CollectibleCredit:
    id: str
    task_id: str
    collectible_id: str
    credit_count: int = 1


@dataclass(frozen=True)
class TravelRegion:
    id: str
    display_name: str
    description: str
    principal_hub: str
    rationale: str
    sort_order: int
    region_type: RegionType
    departure_location_id: str | None = None


@dataclass(frozen=True)
class Location:
    id: str
    display_name: str
    region_id: str
    location_type: LocationType
    content_source: ContentSource
    source_urls: tuple[str, ...]
    assignment_rationale: str
    verification_status: VerificationStatus
    description: str = ""
    aliases: tuple[str, ...] = ()
    gated: bool = False
    one_way: bool = False
    missable: bool = False
    requires_special_access: bool = False
    access_notes: str | None = None
    warning_text: str | None = None


@dataclass(frozen=True)
class Prerequisite:
    type: str
    task_id: str | None = None
    minimum_level: int | None = None
    choice_id: str | None = None
    option: str | None = None
    when_outcome_task_id: str | None = None
    when_outcome: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class ChoiceOption:
    id: str
    label: str
    excludes_options: tuple[str, ...] = ()
    manual_resolution: bool = False


@dataclass(frozen=True)
class Choice:
    id: str
    title: str
    options: dict[str, ChoiceOption]
    source_url: str | None = None


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    objective: str
    geography_type: GeographyType
    planner_behavior: PlannerBehavior
    location_id: str | None = None
    prerequisites: tuple[Prerequisite, ...] = ()
    any_of_task_ids: tuple[str, ...] = ()
    choice_id: str | None = None
    choice_option: str | None = None
    sets_choice: bool = False
    outcome_options: dict[str, str] = field(default_factory=dict)
    applicable_outcome_task_id: str | None = None
    applicable_outcome: str | None = None
    expires_after_task_id: str | None = None
    access_condition_ids: tuple[str, ...] = ()
    required_collectible_ids: tuple[str, ...] = ()
    preparation_for: tuple[str, ...] = ()
    missable: bool = False
    one_way: bool = False
    warning_text: str | None = None
    source_url: str | None = None
    review_note: str | None = None


@dataclass(frozen=True)
class TaskEvaluation:
    task: Task
    status: TaskStatus
    reasons: tuple[str, ...] = ()
    stored_state: TaskStatus | None = None
    derived_exclusion: bool = False


@dataclass(frozen=True)
class PlannerItem:
    id: str
    title: str
    location: Location
    tasks: tuple[TaskEvaluation, ...]
    domain_ids: tuple[str, ...]

    @property
    def warning_text(self) -> str | None:
        if self.location.warning_text:
            return self.location.warning_text
        return next((item.task.warning_text for item in self.tasks if item.task.warning_text), None)


@dataclass(frozen=True)
class CanonicalContent:
    domains: dict[str, CompletionDomain]
    collections: dict[str, Collection]
    stories: dict[str, Story]
    memberships: dict[str, TaskMembership]
    regions: dict[str, TravelRegion]
    locations: dict[str, Location]
    tasks: dict[str, Task]
    choices: dict[str, Choice]
    access_conditions: dict[str, AccessCondition]
    shouts: dict[str, ShoutDefinition]
    shout_credits: dict[str, ShoutCredit]
    collectibles: dict[str, CollectibleDefinition]
    collectible_credits: dict[str, CollectibleCredit]
    theme: dict[str, dict[str, Any]] = field(default_factory=dict)
    fingerprint: str = ""
