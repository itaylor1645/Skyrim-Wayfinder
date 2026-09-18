from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
CANONICAL = ROOT / "src" / "skyrim_wayfinder" / "data" / "canonical"


def load(name: str):
    return json.loads((CANONICAL / name).read_text(encoding="utf-8"))


def save(name: str, value) -> None:
    (CANONICAL / name).write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def upsert(items: list[dict], additions: list[dict]) -> None:
    replacement = {item["id"]: item for item in additions}
    seen = set()
    for index, item in enumerate(items):
        if item["id"] in replacement:
            items[index] = replacement[item["id"]]
            seen.add(item["id"])
    items.extend(item for item in additions if item["id"] not in seen)


MASKS = [
    ("hevnoraak", "Hevnoraak", "valthume", "SKYRIM", None),
    ("krosis", "Krosis", "shearpoint", "SKYRIM", None),
    ("morokei", "Morokei", "labyrinthian", "SKYRIM", None),
    ("nahkriin", "Nahkriin", "skuldafn", "SKYRIM", None),
    ("otar", "Otar", "ragnvald", "SKYRIM", None),
    ("rahgot", "Rahgot", "forelhost", "SKYRIM", None),
    ("vokun", "Vokun", "high_gate_ruins", "SKYRIM", None),
    ("volsung", "Volsung", "volskygge", "SKYRIM", None),
    ("wooden", "Wooden Mask", "bromjunaar_sanctuary", "SKYRIM", None),
    ("konahrik", "Konahrik", "bromjunaar_sanctuary", "SKYRIM", None),
    ("ahzidal", "Ahzidal", "kolbjorn_barrow", "DRAGONBORN", "access_kolbjorn_depths"),
    ("dukaan", "Dukaan", "white_ridge_barrow", "DRAGONBORN", None),
    ("zahkriisos", "Zahkriisos", "raven_rock_mine", "DRAGONBORN", "access_bloodskal_barrow"),
    ("miraak", "Miraak", "apocrypha", "DRAGONBORN", "access_waking_dreams"),
]

CLAWS = [
    ("coral", "Coral Dragon Claw", "SKYRIM"),
    ("diamond", "Diamond Claw", "SKYRIM"),
    ("ebony", "Ebony Claw", "SKYRIM"),
    ("emerald", "Emerald Dragon Claw", "SKYRIM"),
    ("glass", "Glass Claw", "SKYRIM"),
    ("golden", "Golden Claw", "SKYRIM"),
    ("iron", "Iron Claw", "SKYRIM"),
    ("ivory", "Ivory Dragon Claw", "SKYRIM"),
    ("ruby", "Ruby Dragon Claw", "SKYRIM"),
    ("sapphire", "Sapphire Dragon Claw", "SKYRIM"),
    ("amethyst", "Amethyst Claw", "DRAGONBORN"),
]


def main() -> None:
    stories = load("stories.json")
    story_additions = []
    for order, (slug, name, _location, _source, _access) in enumerate(MASKS, 1):
        if slug in {"morokei", "nahkriin"}:
            continue
        story_additions.append({
            "id": f"mask_{slug}", "collection_id": "dragon_priest_masks",
            "display_name": name, "sort_order": order * 10,
            "source_url": f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ', '_')}",
        })
    for order, (slug, name, _source) in enumerate(CLAWS, 1):
        if slug in {"golden", "diamond"}:
            continue
        story_additions.append({
            "id": f"claw_{slug}", "collection_id": "dragon_claws",
            "display_name": name, "sort_order": order * 10,
            "source_url": f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ', '_')}",
        })
    story_additions.append({
        "id": "prep_konahrik_readiness", "collection_id": "set_aside",
        "display_name": "Konahrik Readiness", "sort_order": 20,
        "source_url": "https://en.uesp.net/wiki/Skyrim:Bromjunaar_Sanctuary",
    })
    upsert(stories, story_additions)
    save("stories.json", stories)

    tasks = load("tasks.json")
    by_task = {item["id"]: item for item in tasks}
    mask_tasks = []
    for slug, name, location, _source, access in MASKS:
        task_id = f"mask_{slug}"
        if slug in {"morokei", "nahkriin"}:
            continue
        task = {
            "id": task_id,
            "title": f"Acquire the {name} Mask" if name != "Wooden Mask" else "Acquire the Wooden Mask",
            "objective": f"Acquire the {name} dragon priest mask.",
            "geography_type": "PHYSICAL", "planner_behavior": "REGIONAL_ACTION",
            "location_id": location,
            "source_url": f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ', '_')}",
        }
        if access:
            task["access_condition_ids"] = [access]
        if slug == "konahrik":
            task["objective"] = "Use the Wooden Mask and all eight shrine masks at Bromjunaar Sanctuary to acquire Konahrik."
            task["prerequisites"] = [{
                "type": "preparation_complete", "task_id": "prep_konahrik_masks",
                "description": "Confirm current possession of the Wooden Mask and all eight shrine masks.",
            }]
        if slug == "miraak":
            task.update({
                "objective": "Loot Miraak's mask after defeating him in Apocrypha.",
                "missable": True,
                "warning_text": "Loot Miraak's mask before leaving the summit; Wayfinder cannot infer later whether it was missed.",
            })
        mask_tasks.append(task)

    claw_tasks = [
        ("claw_coral_buy_winterhold", "Acquire the Coral Dragon Claw from Birna", "Obtain the Coral Dragon Claw from Birna in Winterhold.", "winterhold", None, "coral"),
        ("claw_coral_yngol_barrow", "Acquire the Coral Dragon Claw at Yngol Barrow", "Take the Coral Dragon Claw from its pedestal at Yngol Barrow.", "yngol_barrow", None, "coral"),
        ("claw_ebony_korvanjund", "Acquire the Ebony Claw", "Acquire the Ebony Claw in Korvanjund.", "korvanjund", "access_korvanjund", "ebony"),
        ("claw_emerald_reachwater", "Acquire the Emerald Dragon Claw", "Acquire the Emerald Dragon Claw at Reachwater Rock.", "reachwater_rock", None, "emerald"),
        ("claw_glass_forelhost", "Acquire the Glass Claw", "Acquire the Glass Claw in Forelhost.", "forelhost", None, "glass"),
        ("claw_iron_valthume", "Acquire the Iron Claw", "Acquire the Iron Claw in Valthume.", "valthume", None, "iron"),
        ("claw_ivory_folgunthur", "Acquire the Ivory Dragon Claw", "Acquire the Ivory Dragon Claw in Folgunthur.", "folgunthur", None, "ivory"),
        ("claw_ruby_dead_mens_respite", "Acquire the Ruby Dragon Claw", "Acquire the Ruby Dragon Claw in Dead Men's Respite.", "dead_mens_respite", "access_dead_mens_respite", "ruby"),
        ("claw_sapphire_ivarstead", "Acquire the Sapphire Dragon Claw", "Receive the Sapphire Dragon Claw in Ivarstead after completing Wilhelm's investigation.", "ivarstead", "access_sapphire_claw_reward", "sapphire"),
        ("claw_amethyst_left_vahloks_tomb", "Acquire the left half of the Amethyst Claw", "Acquire the left half of the Amethyst Claw in Vahlok's Tomb.", "vahloks_tomb", "access_vahloks_tomb", "amethyst"),
        ("claw_amethyst_right_vahloks_tomb", "Acquire the right half of the Amethyst Claw", "Acquire the right half of the Amethyst Claw in Vahlok's Tomb.", "vahloks_tomb", "access_vahloks_tomb", "amethyst"),
    ]
    new_claw_tasks = []
    for task_id, title, objective, location, access, _slug in claw_tasks:
        task = {
            "id": task_id, "title": title, "objective": objective,
            "geography_type": "PHYSICAL", "planner_behavior": "REGIONAL_ACTION",
            "location_id": location,
            "source_url": "https://en.uesp.net/wiki/Skyrim:Dragon_Claws",
        }
        if access:
            task["access_condition_ids"] = [access]
        new_claw_tasks.append(task)

    prep = {
        "id": "prep_konahrik_masks",
        "title": "Assemble the Wooden Mask and all eight shrine masks",
        "objective": "Confirm you currently possess the Wooden Mask and all eight shrine masks. Prior acquisition alone does not guarantee current possession.",
        "geography_type": "LOCATIONLESS", "planner_behavior": "PREPARATION",
        "required_collectible_ids": [
            f"dragon_priest_mask_{slug}" for slug in
            ("wooden", "hevnoraak", "krosis", "morokei", "nahkriin", "otar", "rahgot", "vokun", "volsung")
        ],
        "preparation_for": ["mask_konahrik"],
        "source_url": "https://en.uesp.net/wiki/Skyrim:Bromjunaar_Sanctuary",
    }
    upsert(tasks, [*mask_tasks, *new_claw_tasks, prep])
    # Supersede the temporary Shroud Hearth access bridge with the real acquisition Task.
    shroud = next(item for item in tasks if item["id"] == "shout_kynes_peace_shroud_hearth_barrow")
    shroud.pop("access_condition_ids", None)
    shroud["prerequisites"] = [{"type": "task_complete", "task_id": "claw_sapphire_ivarstead"}]
    save("tasks.json", tasks)

    memberships = load("task_memberships.json")
    membership_additions = []
    for slug, name, _location, _source, _access in MASKS:
        if slug in {"morokei", "nahkriin"}:
            continue
        membership_additions.append({
            "id": f"tm_mask_{slug}", "task_id": f"mask_{slug}", "story_id": f"mask_{slug}",
            "completion_role": "REQUIRED", "is_primary": True, "sort_order": 10,
        })
    for task_id, _title, _objective, _location, _access, slug in claw_tasks:
        membership_additions.append({
            "id": f"tm_{task_id}", "task_id": task_id, "story_id": f"claw_{slug}",
            "completion_role": "REQUIRED", "is_primary": True,
            "sort_order": 10 if "left" not in task_id and "right" not in task_id else (10 if "left" in task_id else 20),
        })
    membership_additions.append({
        "id": "tm_prep_konahrik_masks", "task_id": "prep_konahrik_masks",
        "story_id": "prep_konahrik_readiness", "completion_role": "REQUIRED",
        "is_primary": True, "sort_order": 10,
    })
    upsert(memberships, membership_additions)
    save("task_memberships.json", memberships)

    access = load("access_conditions.json")
    access = [item for item in access if item["id"] != "access_shroud_hearth_depths"]
    upsert(access, [{
        "id": "access_sapphire_claw_reward",
        "label": "Sapphire Dragon Claw reward is available",
        "description": "Complete Wilhelm's investigation of Shroud Hearth Barrow and receive the Sapphire Dragon Claw.",
        "source_urls": ["https://en.uesp.net/wiki/Skyrim:Lifting_the_Shroud"],
        "content_source": "SKYRIM",
    }])
    save("access_conditions.json", access)

    collectibles = []
    credits = []
    for slug, name, _location, source, _access in MASKS:
        story_id = {"morokei": "mask_labyrinthian", "nahkriin": "mask_skuldafn"}.get(slug, f"mask_{slug}")
        collectible_id = f"dragon_priest_mask_{slug}"
        collectibles.append({
            "id": collectible_id, "collection_id": "dragon_priest_masks", "story_id": story_id,
            "display_name": name, "required_credit_count": 1, "completion_rule": "ALL",
            "content_source": source,
            "source_url": f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ', '_')}",
        })
        credits.append({
            "id": f"credit_{collectible_id}", "task_id": f"mask_{slug}",
            "collectible_id": collectible_id, "credit_count": 1,
        })
    claw_task_ids = {
        "coral": ["claw_coral_buy_winterhold", "claw_coral_yngol_barrow"],
        "diamond": ["claw_diamond_skuldafn"], "ebony": ["claw_ebony_korvanjund"],
        "emerald": ["claw_emerald_reachwater"], "glass": ["claw_glass_forelhost"],
        "golden": ["collectible_golden_claw_recover"], "iron": ["claw_iron_valthume"],
        "ivory": ["claw_ivory_folgunthur"], "ruby": ["claw_ruby_dead_mens_respite"],
        "sapphire": ["claw_sapphire_ivarstead"],
        "amethyst": ["claw_amethyst_left_vahloks_tomb", "claw_amethyst_right_vahloks_tomb"],
    }
    for slug, name, source in CLAWS:
        story_id = {"golden": "claw_golden", "diamond": "claw_diamond"}.get(slug, f"claw_{slug}")
        collectible_id = f"dragon_claw_{slug}"
        collectibles.append({
            "id": collectible_id, "collection_id": "dragon_claws", "story_id": story_id,
            "display_name": name, "required_credit_count": 2 if slug == "amethyst" else 1,
            "completion_rule": "ANY" if slug == "coral" else "ALL", "content_source": source,
            "source_url": f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ', '_')}",
        })
        for index, task_id in enumerate(claw_task_ids[slug], 1):
            credits.append({
                "id": f"credit_{collectible_id}_{index}", "task_id": task_id,
                "collectible_id": collectible_id, "credit_count": 1,
            })
    save("collectibles.json", collectibles)
    save("collectible_credits.json", credits)


if __name__ == "__main__":
    main()
