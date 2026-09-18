from __future__ import annotations

from pathlib import Path

from skyrim_wayfinder.data import load_canonical_content


ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "docs" / "masks-claws-task-audit.md"
REUSED = {
    "collectible_golden_claw_recover", "claw_diamond_skuldafn",
    "mask_morokei", "mask_nahkriin",
}


def render_audit() -> str:
    content = load_canonical_content()
    lines = [
        "# Masks + Claws Task Audit", "",
        "Generated from the canonical dataset. Do not edit by hand.", "",
        f"- Dragon Priest Mask identities: {sum(c.collection_id == 'dragon_priest_masks' for c in content.collectibles.values())}",
        f"- Dragon Claw identities: {sum(c.collection_id == 'dragon_claws' for c in content.collectibles.values())}",
        f"- Collectible definitions: {len(content.collectibles)}",
        f"- Collectible credits: {len(content.collectible_credits)}",
        f"- Distinct acquisition Tasks: {len({c.task_id for c in content.collectible_credits.values()})}",
        f"- Reused acquisition Tasks: {len(REUSED)}", "",
        "| Collection | Collectible | Rule | Required | Acquisition Task(s) | Access / prerequisite |",
        "|---|---|---:|---:|---|---|",
    ]
    for item in sorted(content.collectibles.values(), key=lambda c: (c.collection_id, c.display_name)):
        credits = sorted(
            (credit for credit in content.collectible_credits.values() if credit.collectible_id == item.id),
            key=lambda credit: credit.task_id,
        )
        task_text = "<br>".join(
            f"`{credit.task_id}`{' (reused)' if credit.task_id in REUSED else ''}"
            for credit in credits
        )
        gates = []
        for credit in credits:
            task = content.tasks[credit.task_id]
            gates.extend(f"`{gate}`" for gate in task.access_condition_ids)
            gates.extend(
                f"`{condition.task_id}`" for condition in task.prerequisites
                if condition.task_id
            )
        lines.append(
            f"| {content.collections[item.collection_id].display_name} | {item.display_name} | "
            f"{item.completion_rule.value} | {item.required_credit_count} | {task_text} | "
            f"{'<br>'.join(gates) if gates else 'None'} |"
        )
    lines.extend([
        "", "## Special behavior", "",
        "- Coral Dragon Claw: either distinct acquisition Task supplies its single required credit; completing one derives the unused route as Not Applicable.",
        "- Amethyst Claw: the left and right half Tasks each supply one of two required credits.",
        "- Konahrik: `prep_konahrik_masks` confirms current possession after the nine historic prerequisite identities are complete.",
        "- Nahkriin retains its Sovngarde expiration and Skuldafn one-way warning.",
        "- Miraak is missable and gated by `access_waking_dreams`, with a loot-before-leaving warning and no fabricated expiration.",
        "- Kyne's Peace at Shroud Hearth Barrow now requires `claw_sapphire_ivarstead`; the temporary `access_shroud_hearth_depths` bridge was removed.",
        "", "## Cross-memberships retained", "",
    ])
    for task_id in sorted(REUSED):
        memberships = [m for m in content.memberships.values() if m.task_id == task_id]
        lines.append(
            f"- `{task_id}`: " + ", ".join(f"`{m.story_id}` ({m.completion_role.value})" for m in memberships)
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT.write_text(render_audit(), encoding="utf-8")


if __name__ == "__main__":
    main()
