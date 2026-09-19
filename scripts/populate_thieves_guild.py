"""Apply the Product-approved finite Thieves Guild graph; safe to rerun."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA = ROOT / "src/skyrim_wayfinder/data/canonical"
BASE = "https://en.uesp.net/wiki/Skyrim:"


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def write(name, value):
    (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upsert(items, additions):
    additions = {item["id"]: item for item in additions}
    for index, item in enumerate(items):
        if item["id"] in additions:
            items[index] = additions.pop(item["id"])
    items.extend(additions.values())


def p(task_id):
    return {"type": "task_complete", "task_id": task_id}


def progress(city):
    return {"type": "finite_progress", "finite_progress_id": f"guild_influence_{city}"}


def t(id, title, place, story, *, after=(), source=None, behavior=None, **extra):
    item = {
        "id": id, "title": title, "objective": title + ".",
        "geography_type": "PHYSICAL" if place else "LOCATIONLESS",
        "planner_behavior": behavior or ("REGIONAL_ACTION" if place else "MILESTONE"),
        "source_url": BASE + (source or story.removeprefix("guild_")).replace(" ", "_"),
    }
    if place:
        item["location_id"] = place
    if after:
        item["prerequisites"] = [p(value) if isinstance(value, str) else value for value in after]
    item.update(extra)
    return item


STORIES = [
    ("chance_arrangement", "A Chance Arrangement", "REQUIRED"),
    ("taking_care_business", "Taking Care of Business", "REQUIRED"),
    ("loud_clear", "Loud and Clear", "REQUIRED"),
    ("dampened_spirits", "Dampened Spirits", "REQUIRED"),
    ("scoundrels_folly", "Scoundrel's Folly", "REQUIRED"),
    ("speaking_silence", "Speaking With Silence", "REQUIRED"),
    ("hard_answers", "Hard Answers", "REQUIRED"),
    ("pursuit", "The Pursuit", "REQUIRED"),
    ("trinity_restored", "Trinity Restored", "REQUIRED"),
    ("blindsighted", "Blindsighted", "REQUIRED"),
    ("darkness_returns", "Darkness Returns", "REQUIRED"),
    ("silver_lining", "Silver Lining", "REQUIRED"),
    ("dainty_sload", "The Dainty Sload", "REQUIRED"),
    ("imitation_amnesty", "Imitation Amnesty", "REQUIRED"),
    ("summerset_shadows", "Summerset Shadows", "REQUIRED"),
    ("under_new_management", "Under New Management", "REQUIRED"),
    ("meet_family", "Meet the Family", "OPTIONAL"),
    ("toying_dead", "Toying With The Dead", "OPTIONAL"),
    ("caravan_fence", "Thieves Guild Caravan Fence Quest", "OPTIONAL"),
    ("valds_debt", "Vald's Debt", "OPTIONAL"),
    ("litany_larceny", "The Litany of Larceny", "OPTIONAL"),
]


def tasks():
    a = []
    add = a.append
    # Joining: Brynjolf continues whether the ring scheme succeeds or fails.
    add(t("guild_chance_meet_brynjolf", "Speak with Brynjolf about joining the Guild", "riften", "A_Chance_Arrangement"))
    add(t("guild_chance_attempt", "Attempt Brynjolf's market scheme", "riften", "A_Chance_Arrangement", after=("guild_chance_meet_brynjolf",), outcome_options={"success": "Ring planted", "failed": "Scheme failed; Brynjolf still offers the next job"}))
    add(t("guild_chance_report", "Report the scheme's outcome to Brynjolf", "riften", "A_Chance_Arrangement", after=("guild_chance_attempt",)))
    add(t("guild_business_accept", "Meet Brynjolf in the Ragged Flagon", "ragged_flagon", "Taking_Care_of_Business", after=("guild_chance_report",)))
    for person in ("keerava", "bersi", "haelga"):
        add(t(f"guild_business_{person}", f"Collect {person.title()}'s debt", "riften", "Taking_Care_of_Business", after=("guild_business_accept",)))
    add(t("guild_business_report", "Return the debts to Brynjolf and join the Guild", "ragged_flagon", "Taking_Care_of_Business", after=tuple(f"guild_business_{x}" for x in ("keerava", "bersi", "haelga"))))
    add(t("guild_loud_accept", "Receive the Goldenglow assignment", "ragged_flagon", "Loud_and_Clear", after=("guild_business_report",)))
    add(t("guild_loud_burn_hives", "Burn exactly three Goldenglow beehives", "goldenglow_estate", "Loud_and_Clear", after=("guild_loud_accept",), warning_text="Burn only three hives to satisfy the Guild's assignment."))
    add(t("guild_loud_bill_sale", "Retrieve Goldenglow's bill of sale", "goldenglow_estate", "Loud_and_Clear", after=("guild_loud_accept",)))
    add(t("guild_loud_report", "Report Goldenglow's bill of sale to Brynjolf", "ragged_flagon", "Loud_and_Clear", after=("guild_loud_burn_hives", "guild_loud_bill_sale")))
    add(t("guild_damp_maven", "Discuss Honningbrew with Maven", "riften", "Dampened_Spirits", after=("guild_loud_report",)))
    add(t("guild_damp_mallus", "Coordinate with Mallus near Whiterun", "whiterun", "Dampened_Spirits", after=("guild_damp_maven",)))
    add(t("guild_damp_sabotage", "Sabotage Honningbrew's mead and pest problem", "honningbrew_meadery", "Dampened_Spirits", after=("guild_damp_mallus",)))
    add(t("guild_damp_note", "Witness the tasting and take Sabjorn's promissory note", "honningbrew_meadery", "Dampened_Spirits", after=("guild_damp_sabotage",)))
    add(t("guild_damp_report", "Return the promissory note to Maven", "riften", "Dampened_Spirits", after=("guild_damp_note",)))
    add(t("guild_folly_mercer", "Ask Mercer about Gulum-Ei", "ragged_flagon", "Scoundrel's_Folly", after=("guild_damp_report",)))
    add(t("guild_folly_gulum", "Confront Gulum-Ei in Solitude", "solitude", "Scoundrel's_Folly", after=("guild_folly_mercer",)))
    add(t("guild_folly_follow", "Follow Gulum-Ei through the East Empire warehouse", "east_empire_company_warehouse", "Scoundrel's_Folly", after=("guild_folly_gulum",)))
    add(t("guild_folly_confront", "Extract Gulum-Ei's information", "east_empire_company_warehouse", "Scoundrel's_Folly", after=("guild_folly_follow",)))
    add(t("guild_folly_report", "Report Gulum-Ei's lead to Mercer", "ragged_flagon", "Scoundrel's_Folly", after=("guild_folly_confront",)))
    add(t("guild_snow_meet_mercer", "Meet Mercer outside Snow Veil Sanctum", "snow_veil_sanctum", "Speaking_With_Silence", after=("guild_folly_report",)))
    add(t("guild_snow_open", "Have Mercer open Snow Veil Sanctum", "snow_veil_sanctum", "Speaking_With_Silence", after=("guild_snow_meet_mercer",)))
    add(t("guild_snow_karliah", "Reach Karliah and survive Mercer's betrayal", "snow_veil_sanctum", "Speaking_With_Silence", after=("guild_snow_open",), access_condition_ids=["access_snow_veil_sanctum"]))
    add(t("guild_hard_enthir", "Ask Enthir to identify Gallus's journal", "winterhold", "Hard_Answers", after=("guild_snow_karliah",)))
    add(t("guild_hard_calcelmo", "Copy Calcelmo's Falmer translation", "understone_keep", "Hard_Answers", after=("guild_hard_enthir",)))
    add(t("guild_hard_report", "Return the translation to Enthir and Karliah", "winterhold", "Hard_Answers", after=("guild_hard_calcelmo",)))
    add(t("guild_pursuit_brynjolf", "Show Brynjolf the evidence against Mercer", "ragged_flagon", "The_Pursuit", after=("guild_hard_report",)))
    add(t("guild_pursuit_plans", "Recover Mercer's plans from Riftweald Manor", "riftweald_manor", "The_Pursuit", after=("guild_pursuit_brynjolf",)))
    add(t("guild_pursuit_report", "Bring Mercer's plans to Brynjolf", "ragged_flagon", "The_Pursuit", after=("guild_pursuit_plans",)))
    add(t("guild_trinity_accept", "Agree to Karliah's Nightingale plan", "ragged_flagon", "Trinity_Restored", after=("guild_pursuit_report",)))
    add(t("guild_trinity_armor", "Receive and equip Nightingale Armor", "nightingale_hall", "Trinity_Restored", after=("guild_trinity_accept",)))
    add(t("guild_trinity_oath", "Take the Nightingale oath", "nightingale_hall", "Trinity_Restored", after=("guild_trinity_armor",)))
    add(t("guild_trinity_finish", "Discuss leadership and Mercer's next move", "nightingale_hall", "Trinity_Restored", after=("guild_trinity_oath",)))
    add(t("guild_blind_enter", "Enter Irkngthand with Karliah and Brynjolf", "irkngthand", "Blindsighted", after=("guild_trinity_finish",)))
    add(t("guild_blind_mercer", "Defeat Mercer Frey in Irkngthand", "irkngthand", "Blindsighted", after=("guild_blind_enter",)))
    add(t("guild_blind_escape", "Escape Irkngthand and speak with Karliah", "irkngthand", "Blindsighted", after=("artifact_skeleton_key_acquire",)))
    add(t("guild_dark_enter", "Enter the Twilight Sepulcher", "twilight_sepulcher", "Darkness_Returns", after=("guild_blind_escape",)))
    add(t("guild_dark_path", "Complete the Pilgrim's Path", "twilight_sepulcher", "Darkness_Returns", after=("guild_dark_enter",)))
    add(t("guild_dark_return_key", "Return the Skeleton Key to the Ebonmere", "twilight_sepulcher", "Darkness_Returns", after=("guild_dark_path", "artifact_skeleton_key_acquire")))
    add(t("guild_dark_choose_role", "Choose an initial Nightingale role", "twilight_sepulcher", "Darkness_Returns", after=("guild_dark_return_key",), outcome_options={"shadow": "Agent of Shadow", "subterfuge": "Agent of Subterfuge", "strife": "Agent of Strife"}))
    # Four parallel finite-restoration branches.
    jobs = [
        ("silver", "markarth", "Silver_Lining", [("endon", "Speak with Endon about the stolen mold", "markarth"), ("mold", "Recover the Curious Silver Mold", "pinewatch"), ("return", "Return the mold to Endon", "markarth")]),
        ("sload", "solitude", "The_Dainty_Sload", [("erikur", "Speak with Erikur about the Dainty Sload", "solitude"), ("blue", "Acquire Balmora Blue from Sabine", "the_red_wave"), ("plant", "Plant Balmora Blue aboard the Dainty Sload", "dainty_sload"), ("return", "Report success to Erikur", "solitude")]),
        ("amnesty", "whiterun", "Imitation_Amnesty", [("olfrid", "Speak with Olfrid Battle-Born", "whiterun"), ("letter", "Steal the incriminating letter", "dragonsreach"), ("records", "Alter the Dragonsreach prison registry", "dragonsreach"), ("return", "Report the forged amnesty to Olfrid", "whiterun")]),
        ("shadows", "windhelm", "Summerset_Shadows", [("torsten", "Speak with Torsten Cruel-Sea", "windhelm"), ("niranye", "Question Niranye about the rival thieves", "windhelm"), ("locket", "Defeat Linwe and recover Fjotli's locket", "uttering_hills_cave"), ("return", "Return the locket to Torsten", "windhelm")]),
    ]
    for prefix, city, source, steps in jobs:
        accept = f"guild_{prefix}_accept"
        add(t(accept, f"Accept the {city.title()} special job from Delvin", "ragged_flagon", source, after=("guild_business_report", progress(city))))
        last = accept
        for suffix, title, place in steps:
            identifier = f"guild_{prefix}_{suffix}"
            add(t(identifier, title, place, source, after=(last,)))
            last = identifier
    add(t("guild_management_ceremony", "Attend the Guild Master ceremony", "ragged_flagon", "Under_New_Management", after=("guild_dark_choose_role", "guild_silver_return", "guild_sload_return", "guild_amnesty_return", "guild_shadows_return")))
    add(t("guild_management_rewards", "Receive Guild Master's Armor and leadership rewards", "ragged_flagon", "Under_New_Management", after=("guild_management_ceremony",)))
    # Finite optional Guild side Stories.
    add(t("guild_family_meet", "Meet Delvin and Vex", "ragged_flagon", "Meet_the_Family", after=("guild_business_report",)))
    add(t("guild_family_armor", "Receive Thieves Guild Armor from Tonilia", "ragged_flagon", "Meet_the_Family", after=("guild_family_meet",)))
    add(t("guild_toying_accept", "Ask Vekel about Arondil's journals", "ragged_flagon", "Toying_With_The_Dead", after=("guild_business_report",)))
    add(t("guild_toying_journals", "Recover all four of Arondil's journals", "yngvild", "Toying_With_The_Dead", after=("guild_toying_accept",)))
    add(t("guild_toying_return", "Bring Arondil's journals to Vekel", "ragged_flagon", "Toying_With_The_Dead", after=("guild_toying_journals",)))
    add(t("guild_caravan_accept", "Accept Tonilia's moon sugar delivery", "ragged_flagon", "Thieves_Guild_Caravan_Fence_Quest", after=("guild_business_report",)))
    add(t("guild_caravan_deliver", "Find Ri'saad's caravan and deliver the moon sugar", None, "Thieves_Guild_Caravan_Fence_Quest", after=("guild_caravan_accept",), behavior="OPPORTUNISTIC", objective="Find Ri'saad outside Whiterun or Markarth, or on the route between them, and deliver Tonilia's moon sugar."))
    add(t("guild_caravan_report", "Report the delivery to Tonilia", "ragged_flagon", "Thieves_Guild_Caravan_Fence_Quest", after=("guild_caravan_deliver",)))
    add(t("guild_vald_maven", "Ask Maven to clear Vald's debt", "riften", "Vald%27s_Debt", after=("guild_pursuit_brynjolf",), expires_after_task_id="guild_pursuit_plans"))
    add(t("guild_vald_quill", "Recover the Quill of Gemination from Lake Honrich", "lake_honrich_quill_wreck", "Vald%27s_Debt", after=("guild_vald_maven",), expires_after_task_id="guild_pursuit_plans"))
    add(t("guild_vald_release", "Have Maven release Vald and obtain Mercer's house key", "riften", "Vald%27s_Debt", after=("guild_vald_quill",), expires_after_task_id="guild_pursuit_plans"))
    litany = [
        ("bee", "Queen Bee Statue", "goldenglow_estate", "guild_loud_accept", "guild_loud_clear", None),
        ("decanter", "Honningbrew Decanter", "honningbrew_meadery", "guild_damp_mallus", "guild_dampened_spirits", None),
        ("map", "East Empire Shipping Map", "east_empire_company_warehouse", "guild_folly_gulum", "guild_scoundrels_folly", None),
        ("ship", "Model Ship", "snow_veil_sanctum", "guild_snow_open", "guild_speaking_silence", "guild_snow_karliah"),
        ("cube", "Dwemer Puzzle Cube", "understone_keep", "guild_hard_enthir", "guild_hard_answers", None),
        ("bust", "Bust of the Gray Fox", "riftweald_manor", "guild_pursuit_brynjolf", "guild_pursuit", None),
        ("eye", "Left Eye of the Falmer", "irkngthand", "guild_blind_mercer", "guild_blindsighted", "guild_blind_escape"),
    ]
    for short, name, place, gate, _story, expiry in litany:
        extra = {"warning_text": f"Before you leave: take the {name}. This unique Litany item can be easy to miss during the quest expedition."} if expiry else {}
        add(t(f"guild_litany_{short}", f"Acquire the {name}", place, "The_Litany_of_Larceny", after=(gate,), **extra))
    return a, litany


def main():
    collections = read("collections.json")
    upsert(collections, [{"id": "thieves_guild", "domain_id": "factions_major", "display_name": "Thieves Guild", "sort_order": 35, "source_url": BASE + "Thieves_Guild_(faction)"}])
    write("collections.json", collections)
    stories = read("stories.json")
    upsert(stories, [{"id": "guild_" + key, "collection_id": "thieves_guild", "display_name": title, "classification": classification, "sort_order": (index + 1) * 10, "source_url": BASE + title.replace(" ", "_").replace("'", "%27")} for index, (key, title, classification) in enumerate(STORIES)])
    write("stories.json", stories)
    locations = read("locations.json")
    upsert(locations, [
        {"id": "the_red_wave", "display_name": "The Red Wave", "region_id": "solitude", "location_type": "EXTERIOR_SITE", "content_source": "SKYRIM", "source_urls": [BASE + "Red_Wave"], "assignment_rationale": "The named ship is moored at Solitude docks; Solitude is the practical staging hub.", "verification_status": "VERIFIED"},
        {"id": "lake_honrich_quill_wreck", "display_name": "Lake Honrich — Quill Wreck", "region_id": "riften", "location_type": "EXTERIOR_SITE", "content_source": "SKYRIM", "source_urls": [BASE + "Vald%27s_Debt"], "assignment_rationale": "The fixed underwater quill objective is in Lake Honrich immediately by Riften.", "verification_status": "VERIFIED"},
    ])
    write("locations.json", locations)
    all_tasks = read("tasks.json")
    new_tasks, litany = tasks()
    skeleton = next(item for item in all_tasks if item["id"] == "artifact_skeleton_key_acquire")
    skeleton["prerequisites"] = [p("guild_blind_mercer")]
    upsert(all_tasks, new_tasks)
    write("tasks.json", all_tasks)
    access = read("access_conditions.json")
    next(item for item in access if item["id"] == "access_snow_veil_sanctum")["satisfied_by_any_task_ids"] = ["guild_snow_open"]
    next(item for item in access if item["id"] == "access_blindsighted_irkngthand")["satisfied_by_any_task_ids"] = ["guild_blind_enter"]
    write("access_conditions.json", access)
    members = read("task_memberships.json")
    by_source = {title: "guild_" + key for key, title, _ in STORIES}
    special = {"A_Chance_Arrangement": "chance_arrangement", "Taking_Care_of_Business": "taking_care_business", "Loud_and_Clear": "loud_clear", "Dampened_Spirits": "dampened_spirits", "Scoundrel's_Folly": "scoundrels_folly", "Speaking_With_Silence": "speaking_silence", "Hard_Answers": "hard_answers", "The_Pursuit": "pursuit", "Trinity_Restored": "trinity_restored", "Blindsighted": "blindsighted", "Darkness_Returns": "darkness_returns", "Silver_Lining": "silver_lining", "The_Dainty_Sload": "dainty_sload", "Imitation_Amnesty": "imitation_amnesty", "Summerset_Shadows": "summerset_shadows", "Under_New_Management": "under_new_management", "Meet_the_Family": "meet_family", "Toying_With_The_Dead": "toying_dead", "Thieves_Guild_Caravan_Fence_Quest": "caravan_fence", "Vald%27s_Debt": "valds_debt", "The_Litany_of_Larceny": "litany_larceny"}
    additions = []
    order = {}
    for item in new_tasks:
        source = item["source_url"].removeprefix(BASE)
        story = "guild_" + special[source]
        order[story] = order.get(story, 0) + 10
        additions.append({"id": "tm_" + item["id"], "task_id": item["id"], "story_id": story, "is_primary": True, "completion_role": "REQUIRED", "sort_order": order[story]})
    additions.append({"id": "tm_guild_skeleton_key", "task_id": "artifact_skeleton_key_acquire", "story_id": "guild_blindsighted", "is_primary": False, "completion_role": "REQUIRED", "sort_order": 30})
    additions.append({"id": "tm_guild_snow_disarm", "task_id": "shout_disarm_snow_veil_sanctum", "story_id": "guild_speaking_silence", "is_primary": False, "completion_role": "ASSOCIATED", "sort_order": 25})
    for short, _, _, _, main_story, _ in litany:
        additions.append({"id": "tm_guild_litany_" + short + "_associated", "task_id": "guild_litany_" + short, "story_id": main_story, "is_primary": False, "completion_role": "ASSOCIATED", "sort_order": 90})
    upsert(members, additions)
    write("task_memberships.json", members)
    coverage_path = ROOT / "docs/geography-coverage.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    guild = next(item for item in coverage["domains"] if item["name"] == "Thieves Guild")
    for place in ("the_red_wave", "lake_honrich_quill_wreck"):
        if place not in guild["location_ids"]:
            guild["location_ids"].append(place)
    coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
