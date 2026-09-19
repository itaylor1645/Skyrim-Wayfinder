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
    additions_by_id = {item["id"]: item for item in additions}
    seen = set()
    for index, item in enumerate(items):
        if item["id"] in additions_by_id:
            items[index] = additions_by_id[item["id"]]
            seen.add(item["id"])
    items.extend(item for item in additions if item["id"] not in seen)


def task(
    identifier: str, title: str, objective: str, location: str | None,
    source: str, *, behavior: str = "REGIONAL_ACTION", prerequisites=(),
    any_of=(), minimum_level: int | None = None, access=(), **extra,
) -> dict:
    conditions = list(prerequisites)
    if minimum_level:
        conditions.insert(0, {"type": "minimum_level", "minimum_level": minimum_level})
    result = {
        "id": identifier, "title": title, "objective": objective,
        "geography_type": "PHYSICAL" if location else "LOCATIONLESS",
        "planner_behavior": behavior, "source_url": source,
    }
    if location:
        result["location_id"] = location
    if conditions:
        result["prerequisites"] = conditions
    if any_of:
        result["any_of_task_ids"] = list(any_of)
    if access:
        result["access_condition_ids"] = list(access)
    result.update(extra)
    return result


QUESTS = [
    ("daedric_black_star", "The Black Star", "https://en.uesp.net/wiki/Skyrim:The_Black_Star"),
    ("daedric_boethiahs_calling", "Boethiah's Calling", "https://en.uesp.net/wiki/Skyrim:Boethiah%27s_Calling"),
    ("daedric_best_friend", "A Daedra's Best Friend", "https://en.uesp.net/wiki/Skyrim:A_Daedra%27s_Best_Friend"),
    ("daedric_discerning", "Discerning the Transmundane", "https://en.uesp.net/wiki/Skyrim:Discerning_the_Transmundane"),
    ("daedric_ill_met", "Ill Met by Moonlight", "https://en.uesp.net/wiki/Skyrim:Ill_Met_By_Moonlight"),
    ("daedric_cursed_tribe", "The Cursed Tribe", "https://en.uesp.net/wiki/Skyrim:The_Cursed_Tribe"),
    ("daedric_pieces_past", "Pieces of the Past", "https://en.uesp.net/wiki/Skyrim:Pieces_of_the_Past"),
    ("daedric_whispering_door", "The Whispering Door", "https://en.uesp.net/wiki/Skyrim:The_Whispering_Door"),
    ("artifact_break_dawn", "The Break of Dawn", "https://en.uesp.net/wiki/Skyrim:The_Break_of_Dawn"),
    ("daedric_house_horrors", "The House of Horrors", "https://en.uesp.net/wiki/Skyrim:The_House_of_Horrors"),
    ("daedric_taste_death", "The Taste of Death", "https://en.uesp.net/wiki/Skyrim:The_Taste_of_Death"),
    ("daedric_only_cure", "The Only Cure", "https://en.uesp.net/wiki/Skyrim:The_Only_Cure"),
    ("daedric_night_remember", "A Night to Remember", "https://en.uesp.net/wiki/Skyrim:A_Night_To_Remember"),
    ("daedric_mind_madness", "The Mind of Madness", "https://en.uesp.net/wiki/Skyrim:The_Mind_of_Madness"),
    ("daedric_waking_nightmare", "Waking Nightmare", "https://en.uesp.net/wiki/Skyrim:Waking_Nightmare"),
]


def main() -> None:
    locations = load("locations.json")
    upsert(locations, [
        {
            "id": "broken_tower_redoubt", "display_name": "Broken Tower Redoubt",
            "region_id": "markarth", "location_type": "DUNGEON", "content_source": "SKYRIM",
            "source_urls": ["https://en.uesp.net/wiki/Skyrim:Broken_Tower_Redoubt"],
            "assignment_rationale": "This Reach redoubt is most practically staged from Markarth.",
            "verification_status": "VERIFIED",
        },
        {
            "id": "brucas_leap_redoubt", "display_name": "Bruca's Leap Redoubt",
            "region_id": "markarth", "location_type": "DUNGEON", "content_source": "SKYRIM",
            "source_urls": ["https://en.uesp.net/wiki/Skyrim:Bruca%27s_Leap_Redoubt"],
            "assignment_rationale": "This Reach redoubt is most practically staged from Markarth.",
            "verification_status": "VERIFIED",
        },
        {
            "id": "druadach_redoubt", "display_name": "Druadach Redoubt",
            "region_id": "markarth", "location_type": "DUNGEON", "content_source": "SKYRIM",
            "source_urls": ["https://en.uesp.net/wiki/Skyrim:Druadach_Redoubt"],
            "assignment_rationale": "This Reach redoubt is most practically staged from Markarth.",
            "verification_status": "VERIFIED",
        },
        {
            "id": "hag_rock_redoubt", "display_name": "Hag Rock Redoubt",
            "region_id": "markarth", "location_type": "DUNGEON", "content_source": "SKYRIM",
            "source_urls": ["https://en.uesp.net/wiki/Skyrim:Hag_Rock_Redoubt"],
            "assignment_rationale": "This Reach redoubt is most practically staged from Markarth.",
            "verification_status": "VERIFIED",
        },
        {
            "id": "red_eagle_redoubt", "display_name": "Red Eagle Redoubt",
            "region_id": "markarth", "location_type": "DUNGEON", "content_source": "SKYRIM",
            "source_urls": ["https://en.uesp.net/wiki/Skyrim:Red_Eagle_Redoubt"],
            "assignment_rationale": "This Reach redoubt is most practically staged from Markarth.",
            "verification_status": "VERIFIED",
        },
    ])
    save("locations.json", locations)

    stories = load("stories.json")
    upsert(stories, [
        {"id": sid, "collection_id": "daedric_artifacts", "display_name": name,
         "sort_order": index * 10, "source_url": source}
        for index, (sid, name, source) in enumerate(QUESTS, 1)
    ] + [
        {"id": "artifact_skeleton_key_bridge", "collection_id": "daedric_artifacts",
         "display_name": "Skeleton Key Acquisition", "sort_order": 160,
         "source_url": "https://en.uesp.net/wiki/Skyrim:Skeleton_Key"},
        {"id": "prep_cursed_tribe", "collection_id": "set_aside",
         "display_name": "The Cursed Tribe Ingredients", "sort_order": 30,
         "source_url": "https://en.uesp.net/wiki/Skyrim:The_Cursed_Tribe"},
        {"id": "prep_only_cure", "collection_id": "set_aside",
         "display_name": "The Only Cure Ingredients", "sort_order": 40,
         "source_url": "https://en.uesp.net/wiki/Skyrim:The_Only_Cure"},
    ])
    save("stories.json", stories)

    choices = load("choices.json")
    def binary(identifier, title, left, right, source):
        return {"id": identifier, "title": title, "source_url": source, "options": [
            {"id": left[0], "label": left[1], "excludes_options": [right[0]]},
            {"id": right[0], "label": right[1], "excludes_options": [left[0]]},
        ]}
    upsert(choices, [
        binary("daedric_azura_reward", "The Black Star reward", ("azura", "Restore Azura's Star"), ("black", "Create the Black Star"), QUESTS[0][2]),
        binary("daedric_clavicus_reward", "Clavicus Vile reward", ("masque", "Spare Barbas and receive the Masque"), ("axe", "Kill Barbas and keep the Rueful Axe"), QUESTS[2][2]),
        binary("daedric_hircine_reward", "Hircine reward", ("ring", "Spare Sinding and receive the Ring"), ("hide", "Kill Sinding and receive the Hide"), QUESTS[4][2]),
        binary("daedric_razor_fate", "Mehrunes' Razor outcome", ("razor", "Kill Silus and claim the Razor"), ("spared", "Spare Silus"), QUESTS[6][2]),
        binary("daedric_logrolf_fate", "Logrolf's fate", ("freed", "Free Logrolf"), ("killed", "Kill captive Logrolf"), QUESTS[9][2]),
        binary("daedric_namira_fate", "The Taste of Death outcome", ("ring", "Complete Namira's feast"), ("saved", "Kill Eola and save Verulus"), QUESTS[10][2]),
        binary("daedric_vaermina_fate", "Waking Nightmare outcome", ("skull", "Kill Erandur and take the Skull"), ("destroyed", "Let Erandur destroy the Skull"), QUESTS[14][2]),
    ])
    save("choices.json", choices)

    access = load("access_conditions.json")
    upsert(access, [
        {"id": "access_forsworn_conspiracy_started", "label": "The Forsworn Conspiracy has started",
         "description": "Enter Markarth and begin The Forsworn Conspiracy so Vigilant Tyranus can appear.",
         "source_urls": [QUESTS[9][2]], "content_source": "SKYRIM"},
        {"id": "access_blindsighted_irkngthand", "label": "Blindsighted access to Irkngthand",
         "description": "Advance the Thieves Guild quest Blindsighted until the Skeleton Key can be acquired in Irkngthand.",
         "source_urls": ["https://en.uesp.net/wiki/Skyrim:Blindsighted"], "content_source": "SKYRIM"},
    ])
    save("access_conditions.json", access)

    tasks = load("tasks.json")
    sources = {item[0]: item[2] for item in QUESTS}
    P = lambda task_id: {"type": "task_complete", "task_id": task_id}
    new = []
    # The Black Star
    new += [
        task("daedric_black_star_visit_shrine", "Consult Aranea at the Shrine of Azura", "Ask Aranea about Azura's vision.", "shrine_of_azura", sources["daedric_black_star"]),
        task("daedric_black_star_consult_nelacar", "Consult Nelacar", "Ask Nelacar about Malyn Varen and the broken Star.", "frozen_hearth", sources["daedric_black_star"], prerequisites=[P("daedric_black_star_visit_shrine")]),
        task("daedric_black_star_recover_broken", "Recover the Broken Star", "Recover the Broken Azura's Star from Ilinalta's Deep.", "ilinaltas_deep", sources["daedric_black_star"], prerequisites=[P("daedric_black_star_consult_nelacar")]),
        task("artifact_azuras_star_acquire", "Restore Azura's Star", "Return the Star to Aranea, cleanse it, and receive Azura's Star.", "shrine_of_azura", sources["daedric_black_star"], prerequisites=[P("daedric_black_star_recover_broken")], choice_id="daedric_azura_reward", choice_option="azura", sets_choice=True),
        task("artifact_black_star_acquire", "Create the Black Star", "Return the Star to Nelacar, cleanse it, and receive the Black Star.", "frozen_hearth", sources["daedric_black_star"], prerequisites=[P("daedric_black_star_recover_broken")], choice_id="daedric_azura_reward", choice_option="black", sets_choice=True),
    ]
    # Boethiah
    new += [
        task("daedric_boethiah_reach_sacellum", "Meet Boethiah's cult", "Travel to the Sacellum of Boethiah and speak with the priestess.", "sacellum_of_boethiah", sources["daedric_boethiahs_calling"], minimum_level=30),
        task("daedric_boethiah_sacrifice_follower", "Complete Boethiah's sacrifice", "Lead a willing follower to the Pillar of Sacrifice and complete Boethiah's trial.", "sacellum_of_boethiah", sources["daedric_boethiahs_calling"], prerequisites=[P("daedric_boethiah_reach_sacellum")]),
        task("artifact_ebony_mail_acquire", "Acquire the Ebony Mail", "Defeat Boethiah's champion at Knifepoint Ridge and take the Ebony Mail.", "knifepoint_ridge", sources["daedric_boethiahs_calling"], prerequisites=[P("daedric_boethiah_sacrifice_follower")]),
    ]
    # Clavicus Vile
    new += [
        task("daedric_best_friend_speak_lod", "Ask Lod about the stray dog", "Speak with Lod in Falkreath about the dog outside town.", "falkreath", sources["daedric_best_friend"], minimum_level=10),
        task("daedric_best_friend_meet_barbas", "Meet Barbas", "Find Barbas outside Falkreath and agree to help him.", "falkreath", sources["daedric_best_friend"], prerequisites=[P("daedric_best_friend_speak_lod")]),
        task("daedric_best_friend_find_shrine", "Reach Clavicus Vile's shrine", "Travel with Barbas through Haemar's Shame and speak to Clavicus Vile.", "haemars_shame", sources["daedric_best_friend"], prerequisites=[P("daedric_best_friend_meet_barbas")]),
        task("daedric_best_friend_recover_axe", "Recover the Rueful Axe", "Retrieve the Rueful Axe from Rimerock Burrow.", "rimerock_burrow", sources["daedric_best_friend"], prerequisites=[P("daedric_best_friend_find_shrine")]),
        task("artifact_masque_clavicus_acquire", "Return the Axe and acquire the Masque", "Spare Barbas, return the Rueful Axe, and receive the Masque of Clavicus Vile.", "haemars_shame", sources["daedric_best_friend"], prerequisites=[P("daedric_best_friend_recover_axe")], choice_id="daedric_clavicus_reward", choice_option="masque", sets_choice=True),
        task("artifact_rueful_axe_acquire", "Kill Barbas and keep the Rueful Axe", "Accept Clavicus Vile's bargain, kill Barbas, and retain the Rueful Axe.", "haemars_shame", sources["daedric_best_friend"], prerequisites=[P("daedric_best_friend_recover_axe")], choice_id="daedric_clavicus_reward", choice_option="axe", sets_choice=True),
    ]
    # Discerning the Transmundane and shared Elder Knowledge route
    new += [
        task("daedric_discerning_seek_septimus", "Ask Septimus about the Dwemer lockbox", "Begin Septimus Signus's investigation of the lockbox beneath his outpost.", "septimus_signus_outpost", sources["daedric_discerning"]),
        task("daedric_discerning_return_lexicon", "Return the transcribed Lexicon", "Bring the transcribed Lexicon back to Septimus Signus.", "septimus_signus_outpost", sources["daedric_discerning"], prerequisites=[P("mq_elder_acquire_scroll")]),
        task("daedric_discerning_resume_research", "Resume Septimus's research", "At level 15, speak to Septimus about opening the Dwemer lockbox.", "septimus_signus_outpost", sources["daedric_discerning"], prerequisites=[P("daedric_discerning_return_lexicon")], minimum_level=15),
        task("daedric_discerning_harvest_blood", "Harvest blood from the five elven races", "Opportunistically collect Altmer, Bosmer, Dunmer, Falmer, and Orsimer blood from suitable remains.", None, sources["daedric_discerning"], behavior="OPPORTUNISTIC", prerequisites=[P("daedric_discerning_resume_research")]),
        task("daedric_discerning_deliver_blood", "Deliver the blood samples", "Return the five blood samples to Septimus Signus.", "septimus_signus_outpost", sources["daedric_discerning"], prerequisites=[P("daedric_discerning_harvest_blood")]),
        task("artifact_oghma_infinium_acquire", "Acquire the Oghma Infinium", "Open the Dwemer lockbox and take the Oghma Infinium.", "septimus_signus_outpost", sources["daedric_discerning"], prerequisites=[P("daedric_discerning_deliver_blood")]),
    ]
    # Hircine
    new += [
        task("daedric_ill_met_speak_sinding", "Speak with Sinding", "Speak with Sinding in Falkreath Jail and accept the Cursed Ring.", "falkreath_jail", sources["daedric_ill_met"]),
        task("daedric_ill_met_hunt_stag", "Hunt Hircine's White Stag", "Find the White Stag at its assigned wilderness position and receive Hircine's challenge.", None, sources["daedric_ill_met"], behavior="OPPORTUNISTIC", prerequisites=[P("daedric_ill_met_speak_sinding")]),
        task("artifact_ring_hircine_acquire", "Spare Sinding and acquire the Ring of Hircine", "Help Sinding defeat the hunters and receive the uncursed Ring of Hircine.", "bloated_mans_grotto", sources["daedric_ill_met"], prerequisites=[P("daedric_ill_met_hunt_stag")], choice_id="daedric_hircine_reward", choice_option="ring", sets_choice=True),
        task("artifact_saviors_hide_acquire", "Kill Sinding and acquire Savior's Hide", "Kill and skin Sinding, then receive Savior's Hide from Hircine.", "bloated_mans_grotto", sources["daedric_ill_met"], prerequisites=[P("daedric_ill_met_hunt_stag")], choice_id="daedric_hircine_reward", choice_option="hide", sets_choice=True),
    ]
    # The Cursed Tribe
    new += [
        task("daedric_cursed_defend_largashbur", "Defend Largashbur", "Help the Orcs repel the giant attack and speak with Atub.", "largashbur", sources["daedric_cursed_tribe"], minimum_level=9),
        task("prep_cursed_tribe_ingredients", "Set aside troll fat and a Daedra heart", "Confirm you currently possess one troll fat and one Daedra heart for Atub's ritual.", None, sources["daedric_cursed_tribe"], behavior="PREPARATION", prerequisites=[P("daedric_cursed_defend_largashbur")], preparation_for=["daedric_cursed_complete_ritual"]),
        task("daedric_cursed_complete_ritual", "Complete Atub's ritual", "Bring the ingredients to Atub and witness Malacath's instructions.", "largashbur", sources["daedric_cursed_tribe"], prerequisites=[{"type": "preparation_complete", "task_id": "prep_cursed_tribe_ingredients"}]),
        task("daedric_cursed_defeat_giant", "Defeat the giant in Giant's Grove", "Travel through Fallowstone Cave and recover Shagrol's Warhammer.", "fallowstone_cave", sources["daedric_cursed_tribe"], prerequisites=[P("daedric_cursed_complete_ritual")]),
        task("daedric_cursed_place_hammer", "Place Shagrol's Warhammer on the shrine", "Return to Largashbur and place the warhammer on Malacath's shrine, completing the quest.", "largashbur", sources["daedric_cursed_tribe"], prerequisites=[P("daedric_cursed_defeat_giant")]),
        task("artifact_volendrung_acquire", "Take Volendrung", "Physically take Volendrung from Malacath's shrine after it appears.", "largashbur", sources["daedric_cursed_tribe"], prerequisites=[P("daedric_cursed_place_hammer")]),
    ]
    # Pieces of the Past
    new += [
        task("daedric_pieces_visit_museum", "Visit the Mythic Dawn Museum", "Speak with Silus Vesuius about reconstructing Mehrunes' Razor.", "mythic_dawn_museum", sources["daedric_pieces_past"], minimum_level=20),
        task("daedric_pieces_recover_pommel", "Recover the Razor's pommel", "Recover the pommel stone from Dead Crone Rock.", "dead_crone_rock", sources["daedric_pieces_past"], prerequisites=[P("daedric_pieces_visit_museum")]),
        task("daedric_pieces_recover_shards", "Recover the Razor's blade shards", "Recover the blade shards from Cracked Tusk Keep.", "cracked_tusk_keep", sources["daedric_pieces_past"], prerequisites=[P("daedric_pieces_visit_museum")]),
        task("daedric_pieces_recover_hilt", "Recover the Razor's hilt", "Recover the hilt from Jorgen and Lami's House.", "jorgens_house", sources["daedric_pieces_past"], prerequisites=[P("daedric_pieces_visit_museum")]),
        task("daedric_pieces_return_fragments", "Return the Razor fragments", "Bring all three fragments back to Silus at the museum.", "mythic_dawn_museum", sources["daedric_pieces_past"], prerequisites=[P("daedric_pieces_recover_pommel"), P("daedric_pieces_recover_shards"), P("daedric_pieces_recover_hilt")]),
        task("artifact_mehrunes_razor_acquire", "Kill Silus and acquire Mehrunes' Razor", "Obey Mehrunes Dagon, kill Silus, reforge the Razor, and take it.", "shrine_of_mehrunes_dagon", sources["daedric_pieces_past"], prerequisites=[P("daedric_pieces_return_fragments")], choice_id="daedric_razor_fate", choice_option="razor", sets_choice=True),
        task("daedric_pieces_spare_silus", "Spare Silus", "Refuse Mehrunes Dagon and allow Silus to leave with the broken Razor.", "shrine_of_mehrunes_dagon", sources["daedric_pieces_past"], prerequisites=[P("daedric_pieces_return_fragments")], choice_id="daedric_razor_fate", choice_option="spared", sets_choice=True),
    ]
    # Whispering Door
    new += [
        task("daedric_whisper_hear_rumor", "Ask about Balgruuf's strange children", "Ask for the rumor in Whiterun after completing Dragon Rising.", "whiterun", sources["daedric_whispering_door"], prerequisites=[P("hold_whiterun_thane")], minimum_level=20),
        task("daedric_whisper_investigate_door", "Investigate the Whispering Door", "Speak with Nelkir and investigate the old door beneath Dragonsreach.", "dragonsreach", sources["daedric_whispering_door"], prerequisites=[P("daedric_whisper_hear_rumor")]),
        task("artifact_ebony_blade_acquire", "Acquire the Ebony Blade", "Obtain the key, open the Whispering Door, and take the Ebony Blade.", "dragonsreach", sources["daedric_whispering_door"], prerequisites=[P("daedric_whisper_investigate_door")]),
    ]
    # Break of Dawn
    new += [
        task("daedric_break_return_beacon", "Return Meridia's Beacon", "Take Meridia's Beacon to the Statue to Meridia at Kilkreath.", "kilkreath_temple", sources["artifact_break_dawn"], prerequisites=[P("daedric_break_of_dawn_beacon")]),
        task("artifact_dawnbreaker_acquire", "Acquire Dawnbreaker", "Guide Meridia's light through Kilkreath, defeat Malkoran, and take Dawnbreaker.", "kilkreath_temple", sources["artifact_break_dawn"], prerequisites=[P("daedric_break_return_beacon")]),
    ]
    # House of Horrors
    logrolf_locations = [
        ("broken_tower", "Broken Tower Redoubt", "broken_tower_redoubt"),
        ("brucas_leap", "Bruca's Leap Redoubt", "brucas_leap_redoubt"),
        ("deepwood", "Deepwood Redoubt", "deepwood_redoubt"),
        ("druadach", "Druadach Redoubt", "druadach_redoubt"),
        ("hag_rock", "Hag Rock Redoubt", "hag_rock_redoubt"),
        ("red_eagle", "Red Eagle Redoubt", "red_eagle_redoubt"),
    ]
    new += [
        task("daedric_house_enter_abandoned", "Enter the Abandoned House with Tyranus", "Meet Vigilant Tyranus and investigate Markarth's Abandoned House.", "abandoned_house_markarth", sources["daedric_house_horrors"], access=["access_forsworn_conspiracy_started"]),
        task("daedric_house_record_logrolf_location", "Record Logrolf's assigned prison", "Report which radiant location Skyrim assigned for captive Logrolf.", None, sources["daedric_house_horrors"], behavior="MILESTONE", prerequisites=[P("daedric_house_enter_abandoned")], outcome_options={slug: name for slug, name, _location in logrolf_locations}),
    ]
    free_ids = []
    for slug, name, location in logrolf_locations:
        free_id = f"daedric_house_free_logrolf_{slug}"
        free_ids.append(free_id)
        common = dict(applicable_outcome_task_id="daedric_house_record_logrolf_location", applicable_outcome=slug)
        new.append(task(free_id, f"Free Logrolf at {name}", "Release Logrolf and send him back to Molag Bal's altar.", location, sources["daedric_house_horrors"], prerequisites=[P("daedric_house_record_logrolf_location")], choice_id="daedric_logrolf_fate", choice_option="freed", sets_choice=True, **common))
        new.append(task(f"daedric_house_kill_logrolf_{slug}", f"Kill captive Logrolf at {name}", "Kill Logrolf while he is captive, permanently failing Molag Bal's demand.", location, sources["daedric_house_horrors"], prerequisites=[P("daedric_house_record_logrolf_location")], choice_id="daedric_logrolf_fate", choice_option="killed", sets_choice=True, **common))
    new.append(task("artifact_mace_molag_bal_acquire", "Acquire the Mace of Molag Bal", "Return to the Abandoned House, complete Molag Bal's ritual, and receive the Mace.", "abandoned_house_markarth", sources["daedric_house_horrors"], any_of=free_ids, choice_id="daedric_logrolf_fate", choice_option="freed"))
    # Taste of Death
    new += [
        task("daedric_taste_investigate_hall", "Investigate Markarth's Hall of the Dead", "Speak with Verulus and meet Eola in the Hall of the Dead.", "hall_of_the_dead_markarth", sources["daedric_taste_death"]),
        task("daedric_taste_clear_reachcliff", "Clear Reachcliff Cave", "Clear the way to Namira's shrine for Eola's feast.", "reachcliff_cave", sources["daedric_taste_death"], prerequisites=[P("daedric_taste_investigate_hall")]),
        task("daedric_taste_lure_verulus", "Bring Verulus to Reachcliff Cave", "Convince Brother Verulus to follow you to Namira's shrine.", "hall_of_the_dead_markarth", sources["daedric_taste_death"], prerequisites=[P("daedric_taste_clear_reachcliff")]),
        task("artifact_ring_namira_acquire", "Complete the feast and acquire the Ring of Namira", "Kill Verulus, feed at the altar, and receive the Ring of Namira.", "reachcliff_cave", sources["daedric_taste_death"], prerequisites=[P("daedric_taste_lure_verulus")], choice_id="daedric_namira_fate", choice_option="ring", sets_choice=True),
        task("daedric_taste_save_verulus", "Kill Eola and save Verulus", "Turn against Eola at the feast and save Brother Verulus.", "reachcliff_cave", sources["daedric_taste_death"], prerequisites=[P("daedric_taste_lure_verulus")], choice_id="daedric_namira_fate", choice_option="saved", sets_choice=True),
    ]
    # The Only Cure
    new += [
        task("daedric_only_cure_meet_kesh", "Meet Kesh at the Shrine to Peryite", "Ask Kesh the Clean how to commune with Peryite.", "shrine_to_peryite", sources["daedric_only_cure"], minimum_level=12),
        task("prep_only_cure_ingredients", "Set aside Kesh's incense ingredients", "Confirm you currently possess a flawless ruby, silver ingot, deathbell, and vampire dust.", None, sources["daedric_only_cure"], behavior="PREPARATION", prerequisites=[P("daedric_only_cure_meet_kesh")], preparation_for=["daedric_only_cure_inhale_incense"]),
        task("daedric_only_cure_inhale_incense", "Commune with Peryite", "Bring the ingredients to Kesh and inhale the incense fumes.", "shrine_to_peryite", sources["daedric_only_cure"], prerequisites=[{"type": "preparation_complete", "task_id": "prep_only_cure_ingredients"}]),
        task("daedric_only_cure_kill_orchendor", "Kill Orchendor", "Traverse Bthardamz and kill Orchendor.", "bthardamz", sources["daedric_only_cure"], prerequisites=[P("daedric_only_cure_inhale_incense")]),
        task("artifact_spellbreaker_acquire", "Acquire Spellbreaker", "Return to Peryite's shrine and receive Spellbreaker.", "shrine_to_peryite", sources["daedric_only_cure"], prerequisites=[P("daedric_only_cure_kill_orchendor")]),
    ]
    # A Night to Remember
    new += [
        task("daedric_night_meet_sam", "Meet Sam Guevenne", "After level 14, encounter Sam in the tavern Skyrim selected and win his drinking contest.", None, sources["daedric_night_remember"], behavior="OPPORTUNISTIC", minimum_level=14),
        task("daedric_night_temple_dibella", "Investigate the Temple of Dibella", "Clean up the temple and learn where the night continued.", "temple_of_dibella", sources["daedric_night_remember"], prerequisites=[P("daedric_night_meet_sam")]),
        task("daedric_night_visit_rorikstead", "Investigate Rorikstead", "Speak with Ennis about Gleda and the damage from the previous night.", "rorikstead", sources["daedric_night_remember"], prerequisites=[P("daedric_night_temple_dibella")]),
        task("daedric_night_speak_ysolda", "Ask Ysolda about the wedding", "Resolve Ysolda's demand or learn where Skyrim placed the missing wedding ring.", "whiterun", sources["daedric_night_remember"], prerequisites=[P("daedric_night_visit_rorikstead")], outcome_options={"resolved": "Paid or persuaded Ysolda", "retrieve_ring": "Sent to retrieve the ring"}),
        task("daedric_night_retrieve_ring", "Retrieve the wedding ring", "Recover Ysolda's wedding ring from Moira at Witchmist Grove.", "witchmist_grove", sources["daedric_night_remember"], prerequisites=[P("daedric_night_speak_ysolda")], applicable_outcome_task_id="daedric_night_speak_ysolda", applicable_outcome="retrieve_ring"),
        task("daedric_night_return_ring", "Return the wedding ring to Ysolda", "Return the recovered ring and learn Sam's destination.", "whiterun", sources["daedric_night_remember"], prerequisites=[P("daedric_night_retrieve_ring")], applicable_outcome_task_id="daedric_night_speak_ysolda", applicable_outcome="retrieve_ring"),
        task("daedric_night_reach_portal", "Find Sam's portal", "Traverse Morvunskar and enter the portal to Misty Grove.", "morvunskar", sources["daedric_night_remember"], prerequisites=[P("daedric_night_speak_ysolda"), {"type": "task_complete", "task_id": "daedric_night_return_ring", "when_outcome_task_id": "daedric_night_speak_ysolda", "when_outcome": "retrieve_ring"}]),
        task("artifact_sanguine_rose_acquire", "Acquire the Sanguine Rose", "Confront Sam in Misty Grove and receive the Sanguine Rose.", "misty_grove", sources["daedric_night_remember"], prerequisites=[P("daedric_night_reach_portal")], one_way=True, warning_text="Misty Grove cannot normally be revisited after Sanguine returns you to Skyrim."),
    ]
    # Mind of Madness
    new += [
        task("daedric_mind_speak_dervenin", "Speak with Dervenin", "Ask Dervenin about his missing master in Solitude.", "solitude", sources["daedric_mind_madness"]),
        task("daedric_mind_enter_pelagius_wing", "Enter the Pelagius Wing", "Obtain access and enter the sealed Pelagius Wing of the Blue Palace.", "blue_palace", sources["daedric_mind_madness"], prerequisites=[P("daedric_mind_speak_dervenin")]),
        task("artifact_wabbajack_acquire", "Complete Pelagius's trials and acquire Wabbajack", "Resolve the three trials in Pelagius's mind and receive Wabbajack.", "blue_palace", sources["daedric_mind_madness"], prerequisites=[P("daedric_mind_enter_pelagius_wing")]),
    ]
    # Waking Nightmare
    new += [
        task("daedric_waking_follow_erandur", "Follow Erandur to Nightcaller Temple", "Speak with Erandur at Windpeak Inn and follow him to the temple.", "windpeak_inn", sources["daedric_waking_nightmare"]),
        task("daedric_waking_reach_skull", "Reach the Skull of Corruption", "Traverse Nightcaller Temple, use the Dreamstride, and reach the Skull.", "nightcaller_temple", sources["daedric_waking_nightmare"], prerequisites=[P("daedric_waking_follow_erandur")]),
        task("artifact_skull_corruption_acquire", "Kill Erandur and acquire the Skull of Corruption", "Obey Vaermina, kill Erandur, and take the Skull of Corruption.", "nightcaller_temple", sources["daedric_waking_nightmare"], prerequisites=[P("daedric_waking_reach_skull")], choice_id="daedric_vaermina_fate", choice_option="skull", sets_choice=True),
        task("daedric_waking_destroy_skull", "Allow Erandur to destroy the Skull", "Reject Vaermina's command and let Erandur banish the Skull.", "nightcaller_temple", sources["daedric_waking_nightmare"], prerequisites=[P("daedric_waking_reach_skull")], choice_id="daedric_vaermina_fate", choice_option="destroyed", sets_choice=True),
    ]
    # Skeleton Key acquisition-only bridge
    new += [
        task("artifact_skeleton_key_acquire", "Acquire the Skeleton Key", "Take the Skeleton Key during Blindsighted in Irkngthand.", "irkngthand", "https://en.uesp.net/wiki/Skyrim:Skeleton_Key", access=["access_blindsighted_irkngthand"]),
    ]
    upsert(tasks, new)
    # The shared Elder Knowledge route may be entered from either legitimate storyline.
    consult = next(item for item in tasks if item["id"] == "mq_elder_consult_septimus")
    consult.pop("prerequisites", None)
    consult["any_of_task_ids"] = ["mq_throat_meet_paarthurnax", "daedric_discerning_seek_septimus"]
    save("tasks.json", tasks)

    memberships = load("task_memberships.json")
    task_story = {}
    for item in new:
        identifier = item["id"]
        if identifier.startswith("prep_cursed"):
            task_story[identifier] = "prep_cursed_tribe"
        elif identifier.startswith("prep_only"):
            task_story[identifier] = "prep_only_cure"
        elif identifier.startswith(("daedric_black_star", "artifact_azuras", "artifact_black_star")):
            task_story[identifier] = "daedric_black_star"
        elif identifier.startswith(("daedric_boethiah", "artifact_ebony_mail")):
            task_story[identifier] = "daedric_boethiahs_calling"
        elif identifier.startswith(("daedric_best_friend", "artifact_masque", "artifact_rueful")):
            task_story[identifier] = "daedric_best_friend"
        elif identifier.startswith(("daedric_discerning", "artifact_oghma")):
            task_story[identifier] = "daedric_discerning"
        elif identifier.startswith(("daedric_ill_met", "artifact_ring_hircine", "artifact_saviors")):
            task_story[identifier] = "daedric_ill_met"
        elif identifier.startswith(("daedric_cursed", "artifact_volendrung")):
            task_story[identifier] = "daedric_cursed_tribe"
        elif identifier.startswith(("daedric_pieces", "artifact_mehrunes")):
            task_story[identifier] = "daedric_pieces_past"
        elif identifier.startswith(("daedric_whisper", "artifact_ebony_blade")):
            task_story[identifier] = "daedric_whispering_door"
        elif identifier.startswith(("daedric_break", "artifact_dawnbreaker")):
            task_story[identifier] = "artifact_break_dawn"
        elif identifier.startswith(("daedric_house", "artifact_mace")):
            task_story[identifier] = "daedric_house_horrors"
        elif identifier.startswith(("daedric_taste", "artifact_ring_namira")):
            task_story[identifier] = "daedric_taste_death"
        elif identifier.startswith(("daedric_only", "artifact_spellbreaker")):
            task_story[identifier] = "daedric_only_cure"
        elif identifier.startswith(("daedric_night", "artifact_sanguine")):
            task_story[identifier] = "daedric_night_remember"
        elif identifier.startswith(("daedric_mind", "artifact_wabbajack")):
            task_story[identifier] = "daedric_mind_madness"
        elif identifier.startswith(("daedric_waking", "artifact_skull")):
            task_story[identifier] = "daedric_waking_nightmare"
        elif identifier == "artifact_skeleton_key_acquire":
            task_story[identifier] = "artifact_skeleton_key_bridge"
    additions = []
    for index, (task_id, story_id) in enumerate(task_story.items(), 1):
        additions.append({"id": f"tm_{task_id}", "task_id": task_id, "story_id": story_id,
                          "completion_role": "ASSOCIATED" if task_id == "artifact_volendrung_acquire" else "REQUIRED",
                          "is_primary": True, "sort_order": index * 10})
    # Preparation Tasks also participate in their quest without losing Preparation primacy.
    additions += [
        {"id": "tm_prep_cursed_tribe_quest", "task_id": "prep_cursed_tribe_ingredients", "story_id": "daedric_cursed_tribe", "completion_role": "REQUIRED", "is_primary": False, "sort_order": 20},
        {"id": "tm_prep_only_cure_quest", "task_id": "prep_only_cure_ingredients", "story_id": "daedric_only_cure", "completion_role": "REQUIRED", "is_primary": False, "sort_order": 20},
    ]
    # Shared Elder Knowledge Tasks retain their Main Quest primary membership.
    for index, task_id in enumerate(("mq_elder_consult_septimus", "mq_elder_descend_alftand", "mq_elder_cross_blackreach", "mq_elder_acquire_scroll"), 1):
        additions.append({"id": f"tm_{task_id}_discerning", "task_id": task_id, "story_id": "daedric_discerning", "completion_role": "REQUIRED", "is_primary": False, "sort_order": (index + 1) * 10})
    upsert(memberships, additions)
    save("task_memberships.json", memberships)

    collectibles = load("collectibles.json")
    artifact_specs = [
        ("daedric_azuras_star", "Azura's Star", "daedric_black_star", "artifact_azuras_star_acquire", True, "Skyrim:Azura%27s_Star"),
        ("daedric_black_star", "The Black Star", "daedric_black_star", "artifact_black_star_acquire", True, "Skyrim:The_Black_Star_(item)"),
        ("daedric_ebony_mail", "Ebony Mail", "daedric_boethiahs_calling", "artifact_ebony_mail_acquire", True, "Skyrim:Ebony_Mail"),
        ("daedric_rueful_axe", "The Rueful Axe", "daedric_best_friend", "artifact_rueful_axe_acquire", False, "Skyrim:The_Rueful_Axe"),
        ("daedric_masque_clavicus", "Masque of Clavicus Vile", "daedric_best_friend", "artifact_masque_clavicus_acquire", True, "Skyrim:Masque_of_Clavicus_Vile"),
        ("daedric_oghma_infinium", "Oghma Infinium", "daedric_discerning", "artifact_oghma_infinium_acquire", True, "Skyrim:Oghma_Infinium"),
        ("daedric_ring_hircine", "Ring of Hircine", "daedric_ill_met", "artifact_ring_hircine_acquire", True, "Skyrim:Ring_of_Hircine"),
        ("daedric_saviors_hide", "Savior's Hide", "daedric_ill_met", "artifact_saviors_hide_acquire", True, "Skyrim:Savior%27s_Hide"),
        ("daedric_volendrung", "Volendrung", "daedric_cursed_tribe", "artifact_volendrung_acquire", True, "Skyrim:Volendrung"),
        ("daedric_mehrunes_razor", "Mehrunes' Razor", "daedric_pieces_past", "artifact_mehrunes_razor_acquire", True, "Skyrim:Mehrunes%27_Razor"),
        ("daedric_ebony_blade", "Ebony Blade", "daedric_whispering_door", "artifact_ebony_blade_acquire", True, "Skyrim:Ebony_Blade"),
        ("daedric_dawnbreaker", "Dawnbreaker", "artifact_break_dawn", "artifact_dawnbreaker_acquire", True, "Skyrim:Dawnbreaker"),
        ("daedric_mace_molag_bal", "Mace of Molag Bal", "daedric_house_horrors", "artifact_mace_molag_bal_acquire", True, "Skyrim:Mace_of_Molag_Bal"),
        ("daedric_ring_namira", "Ring of Namira", "daedric_taste_death", "artifact_ring_namira_acquire", True, "Skyrim:Ring_of_Namira"),
        ("daedric_skeleton_key", "Skeleton Key", "artifact_skeleton_key_bridge", "artifact_skeleton_key_acquire", False, "Skyrim:Skeleton_Key"),
        ("daedric_spellbreaker", "Spellbreaker", "daedric_only_cure", "artifact_spellbreaker_acquire", True, "Skyrim:Spellbreaker"),
        ("daedric_sanguine_rose", "Sanguine Rose", "daedric_night_remember", "artifact_sanguine_rose_acquire", True, "Skyrim:Sanguine_Rose"),
        ("daedric_wabbajack", "Wabbajack", "daedric_mind_madness", "artifact_wabbajack_acquire", True, "Skyrim:Wabbajack"),
        ("daedric_skull_corruption", "Skull of Corruption", "daedric_waking_nightmare", "artifact_skull_corruption_acquire", True, "Skyrim:Skull_of_Corruption"),
    ]
    upsert(collectibles, [{
        "id": item_id, "collection_id": "daedric_artifacts", "story_id": story_id,
        "display_name": name, "required_credit_count": 1, "completion_rule": "ALL",
        "content_source": "SKYRIM", "source_url": f"https://en.uesp.net/wiki/{page}",
        "oblivion_walker_eligible": eligible,
    } for item_id, name, story_id, _task_id, eligible, page in artifact_specs])
    save("collectibles.json", collectibles)
    credits = load("collectible_credits.json")
    upsert(credits, [{"id": f"credit_{item_id}", "task_id": task_id,
                      "collectible_id": item_id, "credit_count": 1}
                     for item_id, _name, _story, task_id, _eligible, _page in artifact_specs])
    save("collectible_credits.json", credits)


if __name__ == "__main__":
    main()
