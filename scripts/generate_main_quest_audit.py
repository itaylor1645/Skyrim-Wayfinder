from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from skyrim_wayfinder.data import load_canonical_content
from skyrim_wayfinder.domain import CompletionRole


COLLECTION_ID = "skyrim_main_quest"


def _clean(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_audit() -> str:
    content = load_canonical_content()
    stories = sorted(
        (story for story in content.stories.values() if story.collection_id == COLLECTION_ID),
        key=lambda story: story.sort_order,
    )
    memberships_by_story = defaultdict(list)
    memberships_by_task = defaultdict(list)
    for membership in content.memberships.values():
        memberships_by_story[membership.story_id].append(membership)
        memberships_by_task[membership.task_id].append(membership)

    main_task_ids = {
        membership.task_id
        for story in stories
        for membership in memberships_by_story[story.id]
    }
    main_membership_count = sum(len(memberships_by_story[story.id]) for story in stories)
    cross_category_ids = {
        task_id
        for task_id in main_task_ids
        if any(
            content.stories[item.story_id].collection_id != COLLECTION_ID
            for item in memberships_by_task[task_id]
        )
    }

    lines = [
        "# Main Quest canonical task audit",
        "",
        "> Generated from the canonical dataset by `scripts/generate_main_quest_audit.py`.",
        "",
        "## Scope summary",
        "",
        f"- Stories: **{len(stories)}** (including conditional and optional Stories)",
        f"- Unique Tasks represented under Main Quest: **{len(main_task_ids)}**",
        f"- Main Quest memberships: **{main_membership_count}**",
        f"- Main Quest Tasks with cross-category membership: **{len(cross_category_ids)}**",
        "- Geography corrections made during Increment 2B: **none**",
        "",
        "Only Tasks own geography. Every Region below is derived from `Task.location_id → Location.region_id`.",
        "",
    ]

    for story in stories:
        classification = story.classification.value.title()
        lines.extend([
            f"## {_clean(story.display_name)} ({classification})",
            "",
            f"Story source: [{story.source_url}]({story.source_url})" if story.source_url else "Story source: inherited canonical context.",
            "",
            "| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |",
            "|---|---|---|---|---|---|",
        ])
        memberships = sorted(memberships_by_story[story.id], key=lambda item: item.sort_order)
        for membership in memberships:
            task = content.tasks[membership.task_id]
            if task.location_id:
                location = content.locations[task.location_id]
                region = content.regions[location.region_id]
                geography = f"{location.display_name} → {region.display_name}"
            else:
                geography = "No fixed location"

            prerequisites = []
            for condition in task.prerequisites:
                if condition.type in {"task_complete", "preparation_complete"} and condition.task_id:
                    requirement = content.tasks[condition.task_id].title
                    if condition.when_outcome_task_id:
                        requirement += f" (only for `{condition.when_outcome}` outcome)"
                    prerequisites.append(requirement)
                elif condition.type == "minimum_level":
                    prerequisites.append(f"Level {condition.minimum_level}")
                elif condition.type == "choice":
                    prerequisites.append(f"Choice `{condition.option}`")
            if task.any_of_task_ids:
                alternatives = " / ".join(content.tasks[item].title for item in task.any_of_task_ids)
                prerequisites.append(f"Any one: {alternatives}")
            if task.applicable_outcome_task_id:
                source = content.tasks[task.applicable_outcome_task_id].title
                prerequisites.append(f"Applicable only when {source} → `{task.applicable_outcome}`")
            prerequisite_text = "; ".join(prerequisites) or "None"

            others = []
            for other in sorted(memberships_by_task[task.id], key=lambda item: item.sort_order):
                if other.story_id == story.id:
                    continue
                other_story = content.stories[other.story_id]
                collection = content.collections[other_story.collection_id]
                domain = content.domains[collection.domain_id]
                others.append(
                    f"{domain.display_name} / {collection.display_name} / "
                    f"{other_story.display_name} ({other.completion_role.value})"
                )
            other_text = "; ".join(others) or "—"

            warnings = []
            if task.missable:
                warnings.append("Missable")
            if task.one_way:
                warnings.append("One-way access")
            if task.expires_after_task_id:
                warnings.append(f"Expires after {content.tasks[task.expires_after_task_id].title}")
            if task.warning_text:
                warnings.append(task.warning_text)
            warning_text = "; ".join(warnings) or "—"
            task_label = _clean(task.title)
            if task.source_url:
                task_label = f"[{task_label}]({task.source_url})"
            task_label += f" ({membership.completion_role.value})"
            lines.append(
                "| " + " | ".join(
                    _clean(value)
                    for value in (
                        task_label, geography, prerequisite_text,
                        task.planner_behavior.value, other_text, warning_text,
                    )
                ) + " |"
            )
        lines.append("")

    lines.extend([
        "## Conditional and optional behavior",
        "",
        "### Season Unending",
        "",
        "`Ask the Jarl to Use Dragonsreach` requires the user to record the observed Skyrim outcome. "
        "`TRUCE_REQUIRED` activates the four Season Unending Tasks and makes the truce a prerequisite for capturing Odahviing. "
        "`TRUCE_BYPASSED` leaves those Tasks derived Not Applicable and permits capture after the Jarl step. "
        "No placeholder Civil War Tasks are invented.",
        "",
        "### The Fallen adviser routes",
        "",
        "Paarthurnax, Arngeir, and Esbern are three physical alternatives at their actual Locations. "
        "Completing any one satisfies the Jarl prerequisite and makes the two unused routes derived Not Applicable. "
        "Their prior user state remains stored beneath that derived exclusion.",
        "",
        "### Paarthurnax",
        "",
        "The Story is Optional and cannot block Skyrim Main Quest collection completion. "
        "Task Explorer offers a ledger-only `Resolve as Spared` action; it creates no artificial planner Task. "
        "Spared excludes Kill/Report. Completing Kill after that resolution requires confirmation and changes the resolution to Killed. "
        "Resetting the resolution restores automatic evaluation.",
        "",
        "## One-way destinations",
        "",
        "### Skuldafn",
        "",
        "The required chain is Departure → acquire Diamond Claw → use Diamond Claw → defeat Nahkriin → open portal → enter Sovngarde. "
        "The Nahkriin mask and Storm Call are associated Main Quest objectives but required only in their collectible ledgers. "
        "Both expire to derived Not Applicable if incomplete when Enter Sovngarde completes, while their underlying manual state is preserved. "
        "Skuldafn remains hidden from operational special destinations until departure is complete; departure guidance derives from the Region metadata.",
        "",
        "### Sovngarde",
        "",
        "Sovngarde work remains locked and its special destination hidden until `Enter Sovngarde` is complete. "
        "Call of Valor is represented once and has both required Main Quest and Shout memberships.",
        "",
        "## Completion accounting",
        "",
        "Required memberships define a Story denominator; Associated memberships are contextual only. "
        "Optional Stories do not contribute to parent-collection completion. Conditional Stories contribute only while active. "
        "Derived Not Applicable Tasks are removed from achievable denominators. Overall totals deduplicate by canonical Task ID.",
        "",
        "## Known modeling boundary",
        "",
        "Golden Claw and Bleak Falls shout objectives retain their own objective prerequisites and do not inherit Farengar gating from an Associated Main Quest membership. "
        "Alternate activation details that belong to future Side Quest population are intentionally not fabricated. "
        "No unresolved Main Quest modeling concern or geography correction remains for Increment 2B.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "docs" / "main-quest-task-audit.md"
    target.write_text(render_audit(), encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
