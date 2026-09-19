from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
CANONICAL = ROOT / "src" / "skyrim_wayfinder" / "data" / "canonical"
COVERAGE = ROOT / "docs" / "geography-coverage.json"


def load(name: str):
    return json.loads((CANONICAL / name).read_text(encoding="utf-8"))


def save(name: str, value) -> None:
    (CANONICAL / name).write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def upsert(items: list[dict], additions: list[dict]) -> None:
    additions_by_id = {item["id"]: item for item in additions}
    seen: set[str] = set()
    for index, item in enumerate(items):
        if item["id"] in additions_by_id:
            items[index] = additions_by_id[item["id"]]
            seen.add(item["id"])
    items.extend(item for item in additions if item["id"] not in seen)


def prerequisite(task_id: str, description: str | None = None, *, preparation=False) -> dict:
    result = {
        "type": "preparation_complete" if preparation else "task_complete",
        "task_id": task_id,
    }
    if description:
        result["description"] = description
    return result


def task(
    identifier: str,
    title: str,
    objective: str,
    location_id: str | None,
    source_url: str,
    *,
    prerequisites: tuple[dict, ...] = (),
    behavior: str = "REGIONAL_ACTION",
    access: tuple[str, ...] = (),
    **extra,
) -> dict:
    result = {
        "id": identifier,
        "title": title,
        "objective": objective,
        "geography_type": "PHYSICAL" if location_id else "LOCATIONLESS",
        "planner_behavior": behavior,
        "source_url": source_url,
    }
    if location_id:
        result["location_id"] = location_id
    if prerequisites:
        result["prerequisites"] = list(prerequisites)
    if access:
        result["access_condition_ids"] = list(access)
    result.update(extra)
    return result


SOURCES = {
    "take": "https://en.uesp.net/wiki/Skyrim:Take_Up_Arms",
    "proving": "https://en.uesp.net/wiki/Skyrim:Proving_Honor",
    "silver": "https://en.uesp.net/wiki/Skyrim:The_Silver_Hand",
    "blood": "https://en.uesp.net/wiki/Skyrim:Blood%27s_Honor",
    "revenge": "https://en.uesp.net/wiki/Skyrim:Purity_of_Revenge",
    "glory": "https://en.uesp.net/wiki/Skyrim:Glory_of_the_Dead",
    "totems": "https://en.uesp.net/wiki/Skyrim:Totems_of_Hircine",
    "purity": "https://en.uesp.net/wiki/Skyrim:Purity",
    "lycanthropy": "https://en.uesp.net/wiki/Skyrim:Lycanthropy",
}


STORIES = [
    ("companions_take_up_arms", "Take Up Arms", "REQUIRED", "take"),
    ("companions_proving_honor", "Proving Honor", "REQUIRED", "proving"),
    ("companions_silver_hand", "The Silver Hand", "REQUIRED", "silver"),
    ("companions_bloods_honor", "Blood's Honor", "REQUIRED", "blood"),
    ("companions_purity_revenge", "Purity of Revenge", "REQUIRED", "revenge"),
    ("companions_glory_dead", "Glory of the Dead", "REQUIRED", "glory"),
    ("companions_totems_hircine", "Totems of Hircine", "OPTIONAL", "totems"),
    ("companions_purity_farkas", "Purity — Farkas", "OPTIONAL", "purity"),
    ("companions_purity_vilkas", "Purity — Vilkas", "OPTIONAL", "purity"),
]


def build_tasks() -> list[dict]:
    p = prerequisite
    tasks = [
        task("companions_take_join_trial", "Join the Companions", "Speak with Kodlak and complete the training bout with Vilkas.", "jorrvaskr", SOURCES["take"]),
        task("companions_take_deliver_sword", "Deliver Vilkas's sword", "Take Vilkas's sword to Eorlund Gray-Mane at the Skyforge.", "skyforge", SOURCES["take"], prerequisites=(p("companions_take_join_trial"),)),
        task("companions_take_finish_errands", "Finish the new-member errands", "Deliver Aela's shield and let Farkas show you the living quarters.", "jorrvaskr", SOURCES["take"], prerequisites=(p("companions_take_deliver_sword"),)),
        task("companions_gate_job_after_take", "Complete Skyrim's assigned Companions job", "Complete the radiant job Skyrim assigned after Take Up Arms; Wayfinder does not predict its identity or destination.", None, SOURCES["proving"], prerequisites=(p("companions_take_finish_errands"),), behavior="MILESTONE"),
        task("companions_proving_accept", "Accept Proving Honor", "Speak with Skjor and agree to retrieve a Fragment of Wuuthrad with Farkas.", "jorrvaskr", SOURCES["proving"], prerequisites=(p("companions_gate_job_after_take"),)),
        task("companions_proving_recover_fragment", "Recover the Fragment of Wuuthrad", "Enter Dustman's Cairn with Farkas and recover the Fragment of Wuuthrad.", "dustmans_cairn", SOURCES["proving"], prerequisites=(p("companions_proving_accept"),)),
        task("companions_proving_initiation", "Complete the Companions initiation", "Return to Jorrvaskr and take part in the formal initiation.", "jorrvaskr", SOURCES["proving"], prerequisites=(p("companions_proving_recover_fragment"),)),
        task("companions_gate_job_after_proving", "Complete Skyrim's next assigned Companions job", "Complete the radiant job Skyrim assigned after Proving Honor; Wayfinder does not predict its identity or destination.", None, SOURCES["silver"], prerequisites=(p("companions_proving_initiation"),), behavior="MILESTONE"),
        task("companions_silver_meet_skjor", "Meet Skjor for the Circle initiation", "Speak with Skjor and meet him at the entrance to the Underforge.", "jorrvaskr", SOURCES["silver"], prerequisites=(p("companions_gate_job_after_proving"),)),
        task("companions_silver_become_werewolf", "Become a werewolf in the blood ritual", "Enter the Underforge and accept the Beast Blood required to join the Circle.", "underforge", SOURCES["silver"], prerequisites=(p("companions_silver_meet_skjor"),), sets_access_condition_ids=["companions_lycanthropy_active"]),
        task("companions_silver_clear_gallows", "Defeat the Silver Hand at Gallows Rock", "Fight through Gallows Rock with Aela and discover what happened to Skjor.", "gallows_rock", SOURCES["silver"], prerequisites=(p("companions_silver_become_werewolf"),)),
        task("companions_gate_aela_retaliation", "Complete Aela's first assigned retaliation job", "Complete the first Silver Hand retaliation assignment Skyrim gives through Aela; its identity and destination are radiant.", None, SOURCES["blood"], prerequisites=(p("companions_silver_clear_gallows"),), behavior="MILESTONE"),
        task("companions_gate_second_retaliation", "Complete the second assigned retaliation job", "Complete the second required Silver Hand retaliation assignment; Wayfinder does not predict its identity or destination.", None, SOURCES["blood"], prerequisites=(p("companions_gate_aela_retaliation"),), behavior="MILESTONE"),
        task("companions_blood_accept", "Accept Kodlak's request", "Speak with Kodlak about curing the Companions' lycanthropy.", "jorrvaskr", SOURCES["blood"], prerequisites=(p("companions_gate_second_retaliation"),)),
        task("companions_blood_take_head", "Take a Glenmoril Witch Head", "Defeat a Glenmoril Witch and take the head needed for Kodlak's purification.", "glenmoril_coven", SOURCES["blood"], prerequisites=(p("companions_blood_accept"),)),
        task("companions_blood_collect_spare_heads", "Collect spare Glenmoril Witch Heads", "Optionally defeat the remaining witches and retain spare heads for later purification.", "glenmoril_coven", SOURCES["blood"], prerequisites=(p("companions_blood_take_head"),), warning_text="Spare heads support the player's cure and the two finite Purity quests. Wayfinder does not track inventory quantities."),
        task("companions_blood_return_jorrvaskr", "Return to Kodlak", "Return to Jorrvaskr and discover the aftermath of the Silver Hand attack.", "jorrvaskr", SOURCES["blood"], prerequisites=(p("companions_blood_take_head"),)),
        task("companions_revenge_recover_fragments", "Recover the stolen Wuuthrad fragments", "Enter Driftshade Refuge with Vilkas and recover the stolen Fragments of Wuuthrad.", "driftshade_refuge", SOURCES["revenge"], prerequisites=(p("companions_blood_return_jorrvaskr"),)),
        task("companions_revenge_return_fragments", "Return the Wuuthrad fragments", "Bring the recovered fragments back to Jorrvaskr.", "jorrvaskr", SOURCES["revenge"], prerequisites=(p("companions_revenge_recover_fragments"),)),
        task("companions_glory_attend_funeral", "Attend Kodlak's funeral", "Join the Companions for Kodlak's funeral at the Skyforge.", "skyforge", SOURCES["glory"], prerequisites=(p("companions_revenge_return_fragments"),)),
        task("companions_glory_retrieve_secret_fragment", "Retrieve Kodlak's secret fragment", "Retrieve Kodlak's Fragment of Wuuthrad from his room in Jorrvaskr.", "jorrvaskr", SOURCES["glory"], prerequisites=(p("companions_glory_attend_funeral"),)),
        task("companions_glory_give_fragment_eorlund", "Give Kodlak's fragment to Eorlund", "Return the final Fragment of Wuuthrad to Eorlund at the Skyforge.", "skyforge", SOURCES["glory"], prerequisites=(p("companions_glory_retrieve_secret_fragment"),)),
        task("companions_glory_receive_wuuthrad", "Receive reforged Wuuthrad", "Meet the Circle in the Underforge and receive the reforged Wuuthrad from Eorlund.", "underforge", SOURCES["glory"], prerequisites=(p("companions_glory_give_fragment_eorlund"),)),
        task("companions_glory_open_tomb", "Open Ysgramor's Tomb with Wuuthrad", "Place Wuuthrad on Ysgramor's statue and open the way through the tomb.", "ysgramors_tomb", SOURCES["glory"], prerequisites=(p("companions_glory_receive_wuuthrad"),)),
        task("companions_glory_free_kodlak", "Free Kodlak and become Harbinger", "Use a Glenmoril Witch Head, defeat Kodlak's wolf spirit, and accept the role of Harbinger.", "ysgramors_tomb", SOURCES["glory"], prerequisites=(p("companions_glory_open_tomb"),), sets_access_condition_ids=["access_companions_personal_purification"]),
        task("prep_companions_player_witch_head", "Have a Glenmoril Witch Head available for your cure", "Retain one spare Glenmoril Witch Head if you intend to cure your own lycanthropy.", None, SOURCES["glory"], prerequisites=(p("companions_blood_take_head"),), behavior="PREPARATION", preparation_for=["companions_glory_cure_player"]),
        task("companions_glory_cure_player", "Cure your lycanthropy", "At the Flame of the Harbinger, use a spare Glenmoril Witch Head and defeat your wolf spirit.", "ysgramors_tomb", SOURCES["glory"], prerequisites=(p("companions_glory_free_kodlak"), p("prep_companions_player_witch_head", preparation=True)), access=("companions_lycanthropy_active", "access_companions_personal_purification"), clears_access_condition_ids=["companions_lycanthropy_active", "access_companions_personal_purification"], warning_text="The easiest opportunity is immediately after purifying Kodlak. If you leave without curing yourself, reset the personal-purification access marker; later access may require completing both Purity — Farkas and Purity — Vilkas."),
    ]

    previous = "companions_glory_free_kodlak"
    for number, label in enumerate(("first", "second", "third"), start=1):
        retrieve_id = f"companions_totem_retrieve_{number}"
        place_id = f"companions_totem_place_{number}"
        tasks.append(task(retrieve_id, f"Confirm retrieval of the {label} assigned Totem", f"Complete the Totem retrieval Skyrim assigned. The dungeon is radiant, so Wayfinder records the observed progression without inventing geography.", None, SOURCES["totems"], prerequisites=(p(previous),), behavior="MILESTONE", access=("companions_lycanthropy_active",)))
        tasks.append(task(place_id, f"Place the {label} Totem in the Underforge", f"Return the {label} recovered Totem of Hircine to its receptacle in the Underforge.", "underforge", SOURCES["totems"], prerequisites=(p(retrieve_id),), access=("companions_lycanthropy_active",)))
        previous = place_id

    for member in ("farkas", "vilkas"):
        display = member.title()
        accept_id = f"companions_purity_{member}_accept"
        prep_id = f"prep_companions_{member}_witch_head"
        cure_id = f"companions_purity_{member}_cure"
        tasks.extend([
            task(accept_id, f"Accept {display}'s purification request", f"Speak with {display} at Jorrvaskr and agree to help cure his lycanthropy.", "jorrvaskr", SOURCES["purity"], prerequisites=(p("companions_glory_free_kodlak"),)),
            task(prep_id, f"Have a Glenmoril Witch Head available for {display}", f"Confirm that one spare Glenmoril Witch Head is available for {display}'s purification.", None, SOURCES["purity"], prerequisites=(p(accept_id),), behavior="PREPARATION", preparation_for=[cure_id]),
            task(cure_id, f"Cure {display}'s lycanthropy", f"Take {display} to Ysgramor's Tomb, use a Witch Head, and defeat his wolf spirit.", "ysgramors_tomb", SOURCES["purity"], prerequisites=(p(prep_id, preparation=True),)),
        ])
    return tasks


def main() -> None:
    collections = load("collections.json")
    upsert(collections, [{
        "id": "companions",
        "domain_id": "factions_major",
        "display_name": "Companions",
        "description": "Core Companions progression and finite optional post-story content.",
        "sort_order": 5,
        "source_url": "https://en.uesp.net/wiki/Skyrim:Companions",
    }])
    save("collections.json", collections)

    stories = load("stories.json")
    upsert(stories, [{
        "id": story_id,
        "collection_id": "companions",
        "display_name": display_name,
        "sort_order": index * 10,
        "classification": classification,
        "source_url": SOURCES[source_key],
    } for index, (story_id, display_name, classification, source_key) in enumerate(STORIES, 1)])
    save("stories.json", stories)

    locations = load("locations.json")
    upsert(locations, [{
        "id": "skyforge",
        "display_name": "Skyforge",
        "region_id": "whiterun",
        "location_type": "EXTERIOR_SITE",
        "content_source": "SKYRIM",
        "source_urls": ["https://en.uesp.net/wiki/Skyrim:Skyforge"],
        "assignment_rationale": "The forge is inside Whiterun and is a distinct, recurring Companions destination.",
        "verification_status": "VERIFIED",
    }])
    save("locations.json", locations)

    tasks = load("tasks.json")
    additions = build_tasks()
    upsert(tasks, additions)
    save("tasks.json", tasks)

    access_conditions = load("access_conditions.json")
    by_id = {item["id"]: item for item in access_conditions}
    by_id["access_dustmans_cairn"]["satisfied_by_any_task_ids"] = ["companions_proving_accept"]
    by_id["access_ysgramors_tomb"]["satisfied_by_any_task_ids"] = ["companions_glory_receive_wuuthrad"]
    upsert(access_conditions, [
        {
            "id": "companions_lycanthropy_active",
            "label": "Current Companions lycanthropy",
            "description": "The player currently has Beast Blood. Correct this manually when Skyrim state changes outside the authored Companions tasks.",
            "source_urls": [SOURCES["lycanthropy"]],
            "content_source": "SKYRIM",
        },
        {
            "id": "access_companions_personal_purification",
            "label": "Personal purification is currently available",
            "description": "Available immediately after Kodlak's purification, or later after both Farkas and Vilkas have completed Purity.",
            "source_urls": [SOURCES["glory"], SOURCES["purity"]],
            "content_source": "SKYRIM",
            "satisfied_by_all_task_ids": [
                "companions_purity_farkas_cure",
                "companions_purity_vilkas_cure",
            ],
        },
    ])
    save("access_conditions.json", access_conditions)

    role_by_task = {
        "companions_blood_collect_spare_heads": "ASSOCIATED",
        "prep_companions_player_witch_head": "ASSOCIATED",
        "companions_glory_cure_player": "ASSOCIATED",
    }
    story_by_task: dict[str, str] = {}
    story_prefixes = {
        "companions_take_": "companions_take_up_arms",
        "companions_gate_job_after_take": "companions_proving_honor",
        "companions_proving_": "companions_proving_honor",
        "companions_gate_job_after_proving": "companions_silver_hand",
        "companions_silver_": "companions_silver_hand",
        "companions_gate_aela_": "companions_bloods_honor",
        "companions_gate_second_": "companions_bloods_honor",
        "companions_blood_": "companions_bloods_honor",
        "companions_revenge_": "companions_purity_revenge",
        "companions_glory_": "companions_glory_dead",
        "prep_companions_player_": "companions_glory_dead",
        "companions_totem_": "companions_totems_hircine",
        "companions_purity_farkas_": "companions_purity_farkas",
        "prep_companions_farkas_": "companions_purity_farkas",
        "companions_purity_vilkas_": "companions_purity_vilkas",
        "prep_companions_vilkas_": "companions_purity_vilkas",
    }
    for item in additions:
        matches = [(prefix, story) for prefix, story in story_prefixes.items() if item["id"].startswith(prefix)]
        story_by_task[item["id"]] = max(matches, key=lambda pair: len(pair[0]))[1]

    memberships = load("task_memberships.json")
    order_by_story: dict[str, int] = {}
    new_memberships = []
    for item in additions:
        story_id = story_by_task[item["id"]]
        order_by_story[story_id] = order_by_story.get(story_id, 0) + 10
        new_memberships.append({
            "id": f"tm_{item['id']}",
            "task_id": item["id"],
            "story_id": story_id,
            "completion_role": role_by_task.get(item["id"], "REQUIRED"),
            "is_primary": True,
            "sort_order": order_by_story[story_id],
        })
    new_memberships.extend([
        {
            "id": "tm_shout_fire_breath_dustmans_companions",
            "task_id": "shout_fire_breath_dustmans_cairn",
            "story_id": "companions_proving_honor",
            "completion_role": "ASSOCIATED",
            "is_primary": False,
            "sort_order": 35,
        },
        {
            "id": "tm_shout_animal_allegiance_ysgramors_companions",
            "task_id": "shout_animal_allegiance_ysgramors_tomb",
            "story_id": "companions_glory_dead",
            "completion_role": "ASSOCIATED",
            "is_primary": False,
            "sort_order": 65,
        },
    ])
    upsert(memberships, new_memberships)
    save("task_memberships.json", memberships)

    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    companions = next(item for item in coverage["domains"] if item["name"] == "Companions")
    if "skyforge" not in companions["location_ids"]:
        companions["location_ids"].insert(2, "skyforge")
    COVERAGE.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
