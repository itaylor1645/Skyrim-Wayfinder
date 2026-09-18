from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from skyrim_wayfinder.data import load_canonical_content


REUSED = {
    "shout_unrelenting_force_bleak_falls", "mq_way_voice_high_hrothgar",
    "mq_horn_return_greybeards", "mq_way_voice_whirlwind",
    "shout_become_ethereal_ustengrav", "mq_throat_clear_skies",
    "mq_throat_meet_paarthurnax", "mq_alduins_bane_learn_dragonrend",
    "mq_fallen_plan_paarthurnax", "mq_fallen_plan_arngeir", "mq_fallen_plan_esbern",
    "shout_storm_call_skuldafn", "mq_dragonslayer_call_valor",
}


def render_audit() -> str:
    content = load_canonical_content()
    credits = defaultdict(list)
    for item in content.shout_credits.values():
        credits[item.shout_id].append(item)
    lines = [
        "# Shout canonical task audit", "",
        "> Generated from canonical data by `scripts/generate_shout_audit.py`.", "",
        "## Scope", "",
        f"- Official shouts: **{len(content.shouts)}**",
        f"- Ordered Words of Power: **{sum(len(item.words) for item in content.shouts.values())}**",
        f"- Acquisition Task identities: **{len({item.task_id for item in content.shout_credits.values()})}**",
        f"- Reused Increment 2B Tasks: **{len(REUSED)}**",
        f"- Newly authored Tasks: **{len({item.task_id for item in content.shout_credits.values()} - REUSED)}**",
        f"- AccessConditions: **{len(content.access_conditions)}**", "",
        "Ordinary Word Walls credit the next unlearned word; their Locations are not permanently mapped to a specific rune.", "",
    ]
    for shout in sorted(content.shouts.values(), key=lambda x: content.collections[x.collection_id].sort_order):
        lines += [f"## {shout.display_name}", "", f"Canonical sequence: **{' → '.join(shout.words)}**",
                  f"Source: [{shout.source_url}]({shout.source_url})", "",
                  "| Acquisition Task | Location → Region | Word credit | Gating | Behavior | Cross-memberships / warnings |",
                  "|---|---|---:|---|---|---|"]
        for credit in sorted(credits[shout.id], key=lambda x: content.tasks[x.task_id].title):
            task = content.tasks[credit.task_id]
            if task.location_id:
                loc = content.locations[task.location_id]
                geography = f"{loc.display_name} → {content.regions[loc.region_id].display_name}"
            else:
                geography = "No fixed location"
            gates = [content.access_conditions[x].label for x in task.access_condition_ids]
            gates += [content.tasks[p.task_id].title for p in task.prerequisites if p.task_id]
            memberships = []
            for membership in content.memberships.values():
                if membership.task_id != task.id:
                    continue
                story = content.stories[membership.story_id]
                collection = content.collections[story.collection_id]
                if collection.domain_id != "shouts":
                    memberships.append(f"{collection.display_name} / {story.display_name} ({membership.completion_role.value})")
            notes = memberships
            if task.warning_text: notes.append(task.warning_text)
            lines.append(f"| {task.title} (`{task.id}`) | {geography} | {credit.credit_count} | {'; '.join(gates) or 'None'} | {task.planner_behavior.value} | {'; '.join(notes) or '—'} |")
        lines.append("")
    lines += [
        "## Quest-gated acquisitions", "",
        "AccessConditions are non-completion bridge state for unpopulated questlines. They lock planner recommendations, remain browsable in Explorer, and can be manually satisfied. Existing real Tasks are used where available.", "",
        "## Unusual acquisition behavior", "",
        "- Throw Voice, Clear Skies, Dragonrend, Summon Durnehviir, Call Dragon, and Call of Valor each provide three credits from one actual acquisition event.",
        "- Soul Tear uses three sequential, locationless summons in Tamriel, each worth one credit.",
        "- Battle Fury uses three distinct walls within the single Vahlok's Tomb planning Location.",
        "- Call Dragon credits only the completed adviser route; unused routes are derived Not Applicable.",
        "- Skuldafn's Storm Call credit retains its one-way expiration behavior.",
        "- The known Marked for Death/Drain Vitality engine bug is not modeled as a duplicate canonical shout.", "",
        "## Modeling status", "",
        "No missing geography or unresolved acquisition concern remains. Skyrim, Dawnguard, and Dragonborn participate unconditionally; Creation Club/Anniversary addon shouts are excluded.", "",
    ]
    return "\n".join(lines)


def main():
    target = Path(__file__).resolve().parents[1] / "docs" / "shout-task-audit.md"
    target.write_text(render_audit(), encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__": main()
