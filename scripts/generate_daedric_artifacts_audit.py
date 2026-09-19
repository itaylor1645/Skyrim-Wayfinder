from __future__ import annotations

from pathlib import Path

from skyrim_wayfinder.data import load_canonical_content


ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "docs" / "daedric-artifacts-task-audit.md"
QUEST_STORIES = (
    "daedric_black_star", "daedric_boethiahs_calling", "daedric_best_friend",
    "daedric_discerning", "daedric_ill_met", "daedric_cursed_tribe",
    "daedric_pieces_past", "daedric_whispering_door", "artifact_break_dawn",
    "daedric_house_horrors", "daedric_taste_death", "daedric_only_cure",
    "daedric_night_remember", "daedric_mind_madness", "daedric_waking_nightmare",
)
PRINCES = {
    "daedric_black_star": "Azura", "daedric_boethiahs_calling": "Boethiah",
    "daedric_best_friend": "Clavicus Vile", "daedric_discerning": "Hermaeus Mora",
    "daedric_ill_met": "Hircine", "daedric_cursed_tribe": "Malacath",
    "daedric_pieces_past": "Mehrunes Dagon", "daedric_whispering_door": "Mephala",
    "artifact_break_dawn": "Meridia", "daedric_house_horrors": "Molag Bal",
    "daedric_taste_death": "Namira", "daedric_only_cure": "Peryite",
    "daedric_night_remember": "Sanguine", "daedric_mind_madness": "Sheogorath",
    "daedric_waking_nightmare": "Vaermina",
}
REUSED_TASKS = {
    "daedric_break_of_dawn_beacon", "mq_elder_consult_septimus",
    "mq_elder_descend_alftand", "mq_elder_cross_blackreach", "mq_elder_acquire_scroll",
}


def render_audit() -> str:
    content = load_canonical_content()
    artifacts = [item for item in content.collectibles.values() if item.collection_id == "daedric_artifacts"]
    credits_by_story = {}
    for artifact in artifacts:
        credits_by_story.setdefault(artifact.story_id, []).append(artifact)
    domain_task_ids = {
        membership.task_id for membership in content.memberships.values()
        if membership.story_id in {*QUEST_STORIES, "artifact_skeleton_key_bridge"}
    }
    lines = [
        "# Daedric Artifacts Task Audit", "",
        "Generated from the canonical dataset. Do not edit by hand.", "",
        f"- Standalone Daedric quest Stories: {len(QUEST_STORIES)}",
        "- Skeleton Key acquisition bridges: 1",
        f"- Artifact identities: {len(artifacts)}",
        f"- Oblivion Walker-eligible identities: {sum(item.oblivion_walker_eligible is True for item in artifacts)}",
        f"- Canonical Tasks represented: {len(domain_task_ids)}",
        f"- Reused Tasks: {len(domain_task_ids & REUSED_TASKS)}",
        f"- Newly authored Tasks: {len(domain_task_ids - REUSED_TASKS)}",
        "- Approved geography additions: 5",
        "- Branching choice sets: 7",
        "", "## Quest and task matrix", "",
    ]
    for story_id in QUEST_STORIES:
        story = content.stories[story_id]
        lines += [f"### {story.display_name} — {PRINCES[story_id]}", ""]
        story_memberships = sorted(
            (item for item in content.memberships.values() if item.story_id == story_id),
            key=lambda item: item.sort_order,
        )
        lines += ["| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |", "|---|---|---|---|---|"]
        for membership in story_memberships:
            task = content.tasks[membership.task_id]
            if task.location_id:
                location = content.locations[task.location_id]
                place = f"{location.display_name} / {content.regions[location.region_id].display_name}"
            else:
                place = "No fixed location"
            requirements = []
            for condition in task.prerequisites:
                if condition.type == "minimum_level":
                    requirements.append(f"Level {condition.minimum_level}")
                elif condition.task_id:
                    requirements.append(f"`{condition.task_id}`")
            requirements.extend(f"any: `{item}`" for item in task.any_of_task_ids)
            requirements.extend(f"access: `{item}`" for item in task.access_condition_ids)
            branch = "—"
            if task.choice_id:
                branch = f"`{task.choice_id}` → `{task.choice_option}`"
            elif task.outcome_options:
                branch = "observed outcome: " + ", ".join(task.outcome_options)
            elif task.applicable_outcome_task_id:
                branch = f"when `{task.applicable_outcome_task_id}` = `{task.applicable_outcome}`"
            lines.append(
                f"| `{task.id}` — {task.title} | {task.planner_behavior.value} | {place} | "
                f"{'<br>'.join(requirements) if requirements else 'None'} | {branch} |"
            )
        rewards = credits_by_story.get(story_id, [])
        lines += ["", "Artifacts: " + (", ".join(
            f"**{item.display_name}** ({'eligible' if item.oblivion_walker_eligible else 'not eligible'} for Oblivion Walker; "
            + ", ".join(
                f"credit `{credit.task_id}`" for credit in content.collectible_credits.values()
                if credit.collectible_id == item.id
            ) + ")" for item in rewards
        ) if rewards else "None"), "", f"Source: {story.source_url}", ""]
    skeleton = content.collectibles["daedric_skeleton_key"]
    lines += [
        "## Skeleton Key acquisition bridge", "",
        "The Skeleton Key is tracked through `artifact_skeleton_key_acquire` at Irkngthand, gated by "
        "`access_blindsighted_irkngthand`. The same historical acquisition Task is a REQUIRED secondary membership of Blindsighted; returning the Key in Darkness Returns is a separate faction event and does not undo its collectible credit.", "",
        f"Oblivion Walker eligible: **{'yes' if skeleton.oblivion_walker_eligible else 'no'}**.", "",
        "## Artifact catalog vs Oblivion Walker", "",
        "Wayfinder tracks 19 historically acquired artifact identities. Oblivion Walker recognizes 17 of those identities "
        "and requires 15 qualifying acquisitions. The Rueful Axe and Skeleton Key remain valid Wayfinder collectibles "
        "but are explicitly ineligible. Azura's two rewards and Hircine's two rewards each qualify individually, while "
        "Wayfinder models their intended normal routes as mutually exclusive and does not model exploit-based double rewards.", "",
        "Quest completion and artifact acquisition are separate. In particular, The Cursed Tribe completes when Shagrol's "
        "Warhammer is placed, while `artifact_volendrung_acquire` records physically taking Volendrung afterward.", "",
        "The collection service reports acquired, currently achievable, and full catalog totals separately. Irreversible "
        "recorded choices remove unavailable identities only from the achievable denominator; their catalog entries and "
        "Not Applicable reasons remain inspectable.", "",
        "Primary reference: https://en.uesp.net/wiki/Skyrim:Daedric_Quests", "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUTPUT.write_text(render_audit(), encoding="utf-8")


if __name__ == "__main__":
    main()
