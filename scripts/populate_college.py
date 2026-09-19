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


def prereq(task_id: str, *, preparation=False, when_task=None, when_outcome=None) -> dict:
    result = {
        "type": "preparation_complete" if preparation else "task_complete",
        "task_id": task_id,
    }
    if when_task:
        result["when_outcome_task_id"] = when_task
        result["when_outcome"] = when_outcome
    return result


def task(identifier, title, objective, location, source, *, prerequisites=(), behavior="REGIONAL_ACTION", **extra):
    result = {
        "id": identifier,
        "title": title,
        "objective": objective,
        "geography_type": "PHYSICAL" if location else "LOCATIONLESS",
        "planner_behavior": behavior,
        "source_url": source,
    }
    if location:
        result["location_id"] = location
    if prerequisites:
        result["prerequisites"] = list(prerequisites)
    result.update(extra)
    return result


SOURCES = {
    "first": "https://en.uesp.net/wiki/Skyrim:First_Lessons",
    "saarthal": "https://en.uesp.net/wiki/Skyrim:Under_Saarthal",
    "books": "https://en.uesp.net/wiki/Skyrim:Hitting_the_Books",
    "intentions": "https://en.uesp.net/wiki/Skyrim:Good_Intentions",
    "unseen": "https://en.uesp.net/wiki/Skyrim:Revealing_the_Unseen",
    "containment": "https://en.uesp.net/wiki/Skyrim:Containment",
    "staff": "https://en.uesp.net/wiki/Skyrim:The_Staff_of_Magnus",
    "eye": "https://en.uesp.net/wiki/Skyrim:The_Eye_of_Magnus",
    "arniel": "https://en.uesp.net/wiki/Skyrim:Arniel%27s_Endeavor",
    "brelyna": "https://en.uesp.net/wiki/Skyrim:Brelyna%27s_Practice",
    "jzargo": "https://en.uesp.net/wiki/Skyrim:J%27zargo%27s_Experiment",
    "onmund": "https://en.uesp.net/wiki/Skyrim:Onmund%27s_Request",
    "alteration": "https://en.uesp.net/wiki/Skyrim:Alteration_Ritual_Spell",
    "conjuration": "https://en.uesp.net/wiki/Skyrim:Conjuration_Ritual_Spell",
    "destruction": "https://en.uesp.net/wiki/Skyrim:Destruction_Ritual_Spell",
    "illusion": "https://en.uesp.net/wiki/Skyrim:Illusion_Ritual_Spell",
    "restoration": "https://en.uesp.net/wiki/Skyrim:Restoration_Ritual_Spell",
    "forgotten": "https://en.uesp.net/wiki/Skyrim:Forgotten_Names",
    "equilibrium": "https://en.uesp.net/wiki/Skyrim:Equilibrium",
}


COLLEGE_STORIES = [
    ("college_first_lessons", "First Lessons", "REQUIRED", "first"),
    ("college_under_saarthal", "Under Saarthal", "REQUIRED", "saarthal"),
    ("college_hitting_books", "Hitting the Books", "REQUIRED", "books"),
    ("college_good_intentions", "Good Intentions", "REQUIRED", "intentions"),
    ("college_revealing_unseen", "Revealing the Unseen", "REQUIRED", "unseen"),
    ("college_containment", "Containment", "REQUIRED", "containment"),
    ("college_staff_magnus", "The Staff of Magnus", "REQUIRED", "staff"),
    ("college_eye_magnus", "The Eye of Magnus", "REQUIRED", "eye"),
    ("college_arniels_endeavor", "Arniel's Endeavor", "OPTIONAL", "arniel"),
    ("college_brelynas_practice", "Brelyna's Practice", "OPTIONAL", "brelyna"),
    ("college_jzargos_experiment", "J'zargo's Experiment", "OPTIONAL", "jzargo"),
    ("college_onmunds_request", "Onmund's Request", "OPTIONAL", "onmund"),
    ("college_ritual_alteration", "Alteration Ritual Spell", "OPTIONAL", "alteration"),
    ("college_ritual_conjuration", "Conjuration Ritual Spell", "OPTIONAL", "conjuration"),
    ("college_ritual_destruction", "Destruction Ritual Spell", "OPTIONAL", "destruction"),
    ("college_ritual_illusion", "Illusion Ritual Spell", "OPTIONAL", "illusion"),
    ("college_ritual_restoration", "Restoration Ritual Spell", "OPTIONAL", "restoration"),
    ("college_forgotten_names", "Forgotten Names", "OPTIONAL", "forgotten"),
]


SPELL_STORIES = [
    ("spell_dragonhide", "Dragonhide", "alteration"),
    ("spell_flame_thrall", "Flame Thrall", "conjuration"),
    ("spell_fire_storm", "Fire Storm", "destruction"),
    ("spell_hysteria", "Hysteria", "illusion"),
    ("spell_bane_undead", "Bane of the Undead", "restoration"),
    ("spell_summon_arniels_shade", "Summon Arniel's Shade", "arniel"),
    ("spell_equilibrium", "Equilibrium", "equilibrium"),
    ("spell_vision_tenth_eye", "Vision of the Tenth Eye", "illusion"),
    ("spell_arniels_convection", "Arniel's Convection", "arniel"),
]


def new_tasks() -> list[dict]:
    p = prereq
    result = [
        task("college_under_saarthal_report", "Report the discovery at Saarthal", "Return to the College and report the Eye of Magnus to Arch-Mage Savos Aren.", "college_of_winterhold", SOURCES["saarthal"], prerequisites=(p("college_under_saarthal"),)),
        task("college_hitting_books_accept", "Ask Urag about the stolen books", "Speak with Urag gro-Shub in the Arcanaeum and learn that the stolen books were taken to Fellglow Keep.", "college_of_winterhold", SOURCES["books"], prerequisites=(p("college_under_saarthal_report"),)),
        task("college_hitting_books_return", "Return the stolen books to Urag", "Bring the three recovered books back to Urag at the College.", "college_of_winterhold", SOURCES["books"], prerequisites=(p("college_hitting_books"),)),
        task("college_revealing_unseen_accept", "Accept the Mzulft expedition", "Speak with Mirabelle Ervine and agree to find the Staff of Magnus lead at Mzulft.", "college_of_winterhold", SOURCES["unseen"], prerequisites=(p("college_good_intentions"),)),
        task("college_containment_find_savos", "Find Savos after the explosion", "Reach the College courtyard and find Arch-Mage Savos Aren after Ancano's attack.", "college_of_winterhold", SOURCES["containment"], prerequisites=(p("college_revealing_unseen_report_college"),)),
        task("college_staff_magnus_accept", "Receive the Labyrinthian assignment", "Speak with Mirabelle, receive the Torc of Labyrinthian, and take responsibility for recovering the Staff of Magnus.", "college_of_winterhold", SOURCES["staff"], prerequisites=(p("college_containment_report_college"),)),
        task("college_eye_breach_barrier", "Breach the College barrier", "Return with the Staff of Magnus and use it to open a path into the College.", "college_of_winterhold", SOURCES["eye"], prerequisites=(p("college_staff_magnus"),)),
        task("college_eye_defeat_ancano", "Defeat Ancano and become Arch-Mage", "Use the Staff of Magnus to close the Eye, defeat Ancano, and accept appointment as Arch-Mage.", "college_of_winterhold", SOURCES["eye"], prerequisites=(p("college_eye_breach_barrier"),)),

        task("college_arniel_begin_cogs", "Begin Arniel's project", "Ask Arniel about College business and agree to help with his Dwemer research.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_hitting_books_return"),)),
        task("prep_college_arniel_cogs", "Have ten Dwemer cogs available for Arniel", "Collect and retain ten Dwemer cogs for Arniel's first experiment.", None, SOURCES["arniel"], prerequisites=(p("college_arniel_begin_cogs"),), behavior="PREPARATION", preparation_for=["college_arniel_deliver_cogs"]),
        task("college_arniel_deliver_cogs", "Deliver ten Dwemer cogs", "Bring ten Dwemer cogs to Arniel at the College.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("prep_college_arniel_cogs", preparation=True),)),
        task("college_arniel_negotiate_enthir", "Speak with Enthir for Arniel", "Discuss Arniel's transaction with Enthir and learn what Skyrim assigned for recovery.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_arniel_deliver_cogs"),)),
        task("college_arniel_recover_tandil", "Complete Skyrim's assigned Staff of Tandil recovery", "Recover the Staff of Tandil from the radiant dungeon Skyrim assigned; Wayfinder does not predict its destination.", None, SOURCES["arniel"], prerequisites=(p("college_arniel_negotiate_enthir"),), behavior="MILESTONE"),
        task("college_arniel_deliver_tandil", "Complete Enthir's trade", "Return the Staff of Tandil to Enthir and deliver the warped soul gem to Arniel.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_arniel_recover_tandil"),)),
        task("college_arniel_receive_convection", "Receive Arniel's Convection", "After completing The Eye of Magnus, speak with Arniel and learn Arniel's Convection for the warped soul gem experiment.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_arniel_deliver_tandil"), p("college_eye_defeat_ancano"))),
        task("college_arniel_charge_gem", "Charge the warped soul gem", "Use Skyrim's available Dwemer convectors and Arniel's Convection until the warped soul gem is charged; Wayfinder does not prescribe a convector route.", None, SOURCES["arniel"], prerequisites=(p("college_arniel_receive_convection"),), behavior="MILESTONE"),
        task("college_arniel_return_gem", "Return the charged soul gem", "Bring the charged warped soul gem back to Arniel at the College.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_arniel_charge_gem"),)),
        task("college_arniel_begin_final", "Resume Arniel's project", "After Arniel has had time to continue his work, speak with him and Enthir about the missing delivery.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_arniel_return_gem"),), warning_text="Skyrim normally requires roughly two or three in-game days before this final part becomes available."),
        task("college_arniel_find_courier", "Find Skyrim's assigned courier", "Travel to the radiant location Skyrim assigned and recover the courier's package containing Keening.", None, SOURCES["arniel"], prerequisites=(p("college_arniel_begin_final"),), behavior="MILESTONE"),
        task("college_arniel_receive_shade", "Receive Summon Arniel's Shade", "Return Keening, observe Arniel's final experiment, and receive Summon Arniel's Shade when he disappears.", "college_of_winterhold", SOURCES["arniel"], prerequisites=(p("college_arniel_find_courier"),)),

        task("college_brelyna_accept", "Assist Brelyna's practice", "Agree to let Brelyna practice her experimental spells on you.", "college_of_winterhold", SOURCES["brelyna"], prerequisites=(p("college_under_saarthal_report"),)),
        task("college_brelyna_complete", "Complete Brelyna's spell practice", "Allow Brelyna to complete her successive spell tests after their effects wear off.", "college_of_winterhold", SOURCES["brelyna"], prerequisites=(p("college_brelyna_accept"),)),
        task("college_jzargo_accept", "Receive J'zargo's experimental scrolls", "Agree to test J'zargo's Flame Cloak Scrolls and receive the limited supply of ten scrolls.", "college_of_winterhold", SOURCES["jzargo"], prerequisites=(p("college_under_saarthal_report"),), warning_text="Only ten experimental scrolls are provided. Wasting them without three separately credited undead kills can make this Story impossible."),
        task("college_jzargo_test_scrolls", "Test J'zargo's scrolls on three undead", "Use the experimental scrolls to earn three separately credited undead kills, wherever suitable undead are found.", None, SOURCES["jzargo"], prerequisites=(p("college_jzargo_accept"),), behavior="GLOBAL_ACTION", missable=True, warning_text="The scroll supply is limited. A single activation killing multiple undead may grant only one credit."),
        task("college_jzargo_report", "Report J'zargo's results", "Return to J'zargo and report what his experimental scrolls did.", "college_of_winterhold", SOURCES["jzargo"], prerequisites=(p("college_jzargo_test_scrolls"),)),
        task("college_onmund_negotiate", "Help recover Onmund's amulet", "Speak with Onmund and negotiate with Enthir. Record whether Enthir demands a radiant staff recovery or returns the amulet after persuasion.", "college_of_winterhold", SOURCES["onmund"], prerequisites=(p("college_under_saarthal_report"),), outcome_options={"staff_required": "Enthir requires the Grand Staff of Charming", "persuaded": "Enthir returns the amulet after persuasion"}),
        task("college_onmund_recover_staff", "Complete Skyrim's assigned staff recovery", "Recover the Grand Staff of Charming from the radiant dungeon Skyrim assigned.", None, SOURCES["onmund"], prerequisites=(p("college_onmund_negotiate"),), behavior="MILESTONE", applicable_outcome_task_id="college_onmund_negotiate", applicable_outcome="staff_required"),
        task("college_onmund_return_amulet", "Return Onmund's amulet", "Complete Enthir's terms if required, receive Onmund's amulet, and return it to Onmund.", "college_of_winterhold", SOURCES["onmund"], prerequisites=(p("college_onmund_negotiate"), p("college_onmund_recover_staff", when_task="college_onmund_negotiate", when_outcome="staff_required"))),

        task("college_forgotten_discover", "Investigate the Midden gauntlet", "Discover the strange gauntlet and read the incident report in the Midden Dark.", "college_of_winterhold", SOURCES["forgotten"], prerequisites=(p("college_gain_admission"),), warning_text="Forgotten Names is an unjournaled College secret; Skyrim does not present it as an ordinary quest."),
        task("college_forgotten_recover_rings", "Recover the four ornamental rings", "Use the incident report's key to recover the missing rings from the Arcanaeum.", "college_of_winterhold", SOURCES["forgotten"], prerequisites=(p("college_forgotten_discover"),)),
        task("college_forgotten_resolve", "Resolve Velehk Sain's summoning", "Place the rings on the gauntlet and record whether Velehk Sain was released or killed.", "college_of_winterhold", SOURCES["forgotten"], prerequisites=(p("college_forgotten_recover_rings"),), outcome_options={"released": "Released Velehk Sain", "killed": "Killed Velehk Sain"}, warning_text="This is an unjournaled one-time College secret with an irreversible observed outcome."),
    ]

    ritual_specs = [
        ("alteration", 90, "college_good_intentions", "Tolfdir", "Dragonhide"),
        ("conjuration", 90, "college_gain_admission", "Phinis Gestor", "Flame Thrall"),
        ("destruction", 100, "college_gain_admission", "Faralda", "Fire Storm"),
        ("illusion", 100, "college_gain_admission", "Drevis Neloren", "Hysteria"),
        ("restoration", 90, "college_good_intentions", "Colette Marence", "Bane of the Undead"),
    ]
    for school, level, prior, teacher, reward in ritual_specs:
        note = f"Official unmodified Skyrim requirement: {school.title()} {level}. Mark this when the ritual dialogue is available in the current game."
        if school in {"destruction", "illusion"}:
            note += " Modded setups such as USSEP may lower the dialogue threshold."
        result.append(task(f"college_ritual_{school}_unlock", f"Unlock the {school.title()} ritual dialogue", note, None, SOURCES[school], prerequisites=(p(prior),), behavior="MILESTONE", warning_text="If the skill is later reset to Legendary and Skyrim temporarily blocks progress, use the existing Blocked state; completed historical milestones are not reset."))

    result.extend([
        task("college_ritual_alteration_accept", "Begin the Alteration ritual", "Ask Tolfdir about advanced Alteration research and agree to obtain dragon heartscales.", "college_of_winterhold", SOURCES["alteration"], prerequisites=(p("college_ritual_alteration_unlock"),)),
        task("college_ritual_alteration_fang", "Recover Kahvozein's Fang from Skyrim's assigned dungeon", "Obtain Kahvozein's Fang from the radiant dragon-priest dungeon Skyrim selected.", None, SOURCES["alteration"], prerequisites=(p("college_ritual_alteration_accept"),), behavior="MILESTONE"),
        task("college_ritual_alteration_scales", "Harvest dragon heartscales", "Use Kahvozein's Fang to harvest heartscales from a suitable dragon corpse.", None, SOURCES["alteration"], prerequisites=(p("college_ritual_alteration_fang"),), behavior="GLOBAL_ACTION"),
        task("college_ritual_alteration_dragonhide", "Receive Dragonhide", "Return the heartscales to Tolfdir and receive the unique Dragonhide spell tome.", "college_of_winterhold", SOURCES["alteration"], prerequisites=(p("college_ritual_alteration_scales"),)),
        task("college_ritual_conjuration_accept", "Begin the Conjuration ritual", "Speak with Phinis and receive the temporary Summon Unbound Dremora ritual spell.", "college_of_winterhold", SOURCES["conjuration"], prerequisites=(p("college_ritual_conjuration_unlock"),)),
        task("college_ritual_conjuration_sigil", "Obtain the Sigil Stone", "Summon and defeat the Unbound Dremora as required, then command it to bring a Sigil Stone.", "college_of_winterhold", SOURCES["conjuration"], prerequisites=(p("college_ritual_conjuration_accept"),)),
        task("college_ritual_conjuration_flame_thrall", "Receive Flame Thrall", "Deliver the Sigil Stone to Phinis and receive the unique Flame Thrall spell tome.", "college_of_winterhold", SOURCES["conjuration"], prerequisites=(p("college_ritual_conjuration_sigil"),)),
        task("college_ritual_destruction_book", "Receive Power of the Elements", "Ask Faralda about advanced Destruction and receive the incomplete ritual book.", "college_of_winterhold", SOURCES["destruction"], prerequisites=(p("college_ritual_destruction_unlock"),)),
        task("college_ritual_destruction_windward", "Complete the fire pedestal", "Place Power of the Elements at Windward Ruins and strike the pedestal with fire magic.", "windward_ruins", SOURCES["destruction"], prerequisites=(p("college_ritual_destruction_book"),)),
        task("college_ritual_destruction_skybound", "Complete the frost pedestal", "Take the altered book to North Skybound Watch and strike the pedestal with frost magic.", "north_skybound_watch", SOURCES["destruction"], prerequisites=(p("college_ritual_destruction_windward"),)),
        task("college_ritual_destruction_fire_storm", "Acquire Fire Storm", "Complete the shock pedestal at Four Skull Lookout and read the finished book to learn Fire Storm.", "four_skull_lookout", SOURCES["destruction"], prerequisites=(p("college_ritual_destruction_skybound"),)),
        task("college_ritual_illusion_vision", "Receive Vision of the Tenth Eye", "Speak with Drevis and receive the permanent unique Vision of the Tenth Eye spell.", "college_of_winterhold", SOURCES["illusion"], prerequisites=(p("college_ritual_illusion_unlock"),)),
        task("college_ritual_illusion_texts", "Find the four Master Illusion texts", "Use Vision of the Tenth Eye to find all four hidden texts around the College and Midden.", "college_of_winterhold", SOURCES["illusion"], prerequisites=(p("college_ritual_illusion_vision"),)),
        task("college_ritual_illusion_hysteria", "Receive Hysteria", "Return all four texts to Drevis and receive the unique Hysteria spell tome.", "college_of_winterhold", SOURCES["illusion"], prerequisites=(p("college_ritual_illusion_texts"),)),
        task("college_ritual_restoration_accept", "Begin the Restoration ritual", "Ask Colette about advanced Restoration and receive directions to the Augur of Dunlain.", "college_of_winterhold", SOURCES["restoration"], prerequisites=(p("college_ritual_restoration_unlock"),)),
        task("college_ritual_restoration_bane", "Receive Bane of the Undead", "Pass the Augur's Restoration trial in the Midden and receive Bane of the Undead.", "college_of_winterhold", SOURCES["restoration"], prerequisites=(p("college_ritual_restoration_accept"),)),
        task("spell_equilibrium_labyrinthian", "Acquire Equilibrium", "Collect the unique Equilibrium spell tome while exploring Labyrinthian.", "labyrinthian", SOURCES["equilibrium"], prerequisites=(p("college_staff_magnus_accept"),)),
    ])
    return result


def main() -> None:
    collections = load("collections.json")
    upsert(collections, [{
        "id": "unique_spells",
        "domain_id": "unique_spells_powers",
        "display_name": "Unique Spells",
        "description": "Unique, non-purchasable permanent spell acquisitions.",
        "sort_order": 10,
        "source_url": "https://en.uesp.net/wiki/Skyrim:Spells",
    }])
    save("collections.json", collections)

    stories = load("stories.json")
    upsert(stories, [{
        "id": story_id, "collection_id": "college_winterhold", "display_name": name,
        "sort_order": index * 10, "classification": classification,
        "source_url": SOURCES[source_key],
    } for index, (story_id, name, classification, source_key) in enumerate(COLLEGE_STORIES, 1)])
    upsert(stories, [{
        "id": story_id, "collection_id": "unique_spells", "display_name": name,
        "sort_order": index * 10, "source_url": SOURCES[source_key],
    } for index, (story_id, name, source_key) in enumerate(SPELL_STORIES, 1)])
    save("stories.json", stories)

    locations = load("locations.json")
    upsert(locations, [
        {"id": "windward_ruins", "display_name": "Windward Ruins", "region_id": "dawnstar", "location_type": "EXTERIOR_SITE", "content_source": "SKYRIM", "source_urls": ["https://en.uesp.net/wiki/Skyrim:Windward_Ruins"], "assignment_rationale": "The ritual site lies immediately southwest of Dawnstar and is naturally staged from that city.", "verification_status": "VERIFIED"},
        {"id": "north_skybound_watch", "display_name": "North Skybound Watch", "region_id": "falkreath", "location_type": "EXTERIOR_SITE", "content_source": "SKYRIM", "source_urls": ["https://en.uesp.net/wiki/Skyrim:North_Skybound_Watch"], "assignment_rationale": "The Helgen and Orphan Rock-side approach makes Falkreath the consistent Survival staging region.", "verification_status": "VERIFIED"},
        {"id": "four_skull_lookout", "display_name": "Four Skull Lookout", "region_id": "markarth", "location_type": "EXTERIOR_SITE", "content_source": "SKYRIM", "source_urls": ["https://en.uesp.net/wiki/Skyrim:Four_Skull_Lookout"], "assignment_rationale": "This Karthwasten-area ritual site is naturally staged from Markarth.", "verification_status": "VERIFIED"},
    ])
    save("locations.json", locations)

    tasks = load("tasks.json")
    by_id = {item["id"]: item for item in tasks}
    by_id["college_hitting_books"]["prerequisites"] = [prereq("college_hitting_books_accept")]
    by_id["college_good_intentions"]["objective"] = "Consult the Augur of Dunlain in the Midden and report his warning to Savos Aren."
    by_id["college_good_intentions"]["prerequisites"] = [prereq("college_hitting_books_return")]
    by_id["college_revealing_unseen_mzulft"]["prerequisites"] = [prereq("college_revealing_unseen_accept")]
    by_id["college_containment_defend_winterhold"]["prerequisites"] = [prereq("college_containment_find_savos")]
    by_id["college_staff_magnus"]["prerequisites"] = [prereq("college_staff_magnus_accept")]
    by_id["mask_morokei"]["prerequisites"] = [prereq("college_staff_magnus_accept")]
    by_id["shout_slow_time_labyrinthian"]["prerequisites"] = [prereq("college_staff_magnus_accept")]
    additions = new_tasks()
    upsert(tasks, additions)
    save("tasks.json", tasks)

    access = load("access_conditions.json")
    next(item for item in access if item["id"] == "access_saarthal")["satisfied_by_any_task_ids"] = ["college_first_lessons"]
    save("access_conditions.json", access)

    memberships = load("task_memberships.json")
    # Preserve existing identities while inserting the newly explicit core steps in geographic order.
    existing_orders = {
        "tm_college_admission": 10, "tm_college_first_lessons": 20,
        "tm_college_under_saarthal": 10, "tm_college_hitting_books": 20,
        "tm_college_good_intentions": 10, "tm_college_revealing_mzulft": 20,
        "tm_college_revealing_report": 30, "tm_college_containment_defend": 20,
        "tm_college_containment_report": 30, "tm_college_staff": 20,
        "tm_mask_morokei_college": 30,
    }
    for item in memberships:
        if item["id"] in existing_orders:
            item["sort_order"] = existing_orders[item["id"]]

    task_story = {
        "college_under_saarthal_report": "college_under_saarthal",
        "college_hitting_books_accept": "college_hitting_books",
        "college_hitting_books_return": "college_hitting_books",
        "college_revealing_unseen_accept": "college_revealing_unseen",
        "college_containment_find_savos": "college_containment",
        "college_staff_magnus_accept": "college_staff_magnus",
        "college_eye_breach_barrier": "college_eye_magnus",
        "college_eye_defeat_ancano": "college_eye_magnus",
    }
    prefix_story = {
        "college_arniel_": "college_arniels_endeavor", "prep_college_arniel_": "college_arniels_endeavor",
        "college_brelyna_": "college_brelynas_practice", "college_jzargo_": "college_jzargos_experiment",
        "college_onmund_": "college_onmunds_request", "college_forgotten_": "college_forgotten_names",
        "college_ritual_alteration_": "college_ritual_alteration", "college_ritual_conjuration_": "college_ritual_conjuration",
        "college_ritual_destruction_": "college_ritual_destruction", "college_ritual_illusion_": "college_ritual_illusion",
        "college_ritual_restoration_": "college_ritual_restoration",
    }
    for item in additions:
        if item["id"] == "spell_equilibrium_labyrinthian":
            continue
        if item["id"] not in task_story:
            matches = [(prefix, story) for prefix, story in prefix_story.items() if item["id"].startswith(prefix)]
            task_story[item["id"]] = max(matches, key=lambda pair: len(pair[0]))[1]
    order: dict[str, int] = {}
    new_memberships = []
    explicit_orders = {
        "college_under_saarthal_report": 20, "college_hitting_books_accept": 10,
        "college_hitting_books_return": 30, "college_revealing_unseen_accept": 10,
        "college_containment_find_savos": 10, "college_staff_magnus_accept": 10,
    }
    for item in additions:
        if item["id"] == "spell_equilibrium_labyrinthian":
            continue
        story_id = task_story[item["id"]]
        order[story_id] = order.get(story_id, 0) + 10
        new_memberships.append({
            "id": f"tm_{item['id']}", "task_id": item["id"], "story_id": story_id,
            "completion_role": "REQUIRED", "is_primary": True,
            "sort_order": explicit_orders.get(item["id"], order[story_id]),
        })
    new_memberships.extend([
        {"id": "tm_shout_ice_form_saarthal_college", "task_id": "shout_ice_form_saarthal", "story_id": "college_under_saarthal", "completion_role": "ASSOCIATED", "is_primary": False, "sort_order": 15},
        {"id": "tm_shout_slow_time_labyrinthian_college", "task_id": "shout_slow_time_labyrinthian", "story_id": "college_staff_magnus", "completion_role": "ASSOCIATED", "is_primary": False, "sort_order": 40},
        {"id": "tm_spell_equilibrium_college", "task_id": "spell_equilibrium_labyrinthian", "story_id": "college_staff_magnus", "completion_role": "ASSOCIATED", "is_primary": False, "sort_order": 50},
    ])
    spell_tasks = {
        "spell_dragonhide": "college_ritual_alteration_dragonhide",
        "spell_flame_thrall": "college_ritual_conjuration_flame_thrall",
        "spell_fire_storm": "college_ritual_destruction_fire_storm",
        "spell_hysteria": "college_ritual_illusion_hysteria",
        "spell_bane_undead": "college_ritual_restoration_bane",
        "spell_summon_arniels_shade": "college_arniel_receive_shade",
        "spell_equilibrium": "spell_equilibrium_labyrinthian",
        "spell_vision_tenth_eye": "college_ritual_illusion_vision",
        "spell_arniels_convection": "college_arniel_receive_convection",
    }
    for story_id, task_id in spell_tasks.items():
        new_memberships.append({
            "id": f"tm_{story_id}_acquire", "task_id": task_id, "story_id": story_id,
            "completion_role": "REQUIRED", "is_primary": task_id == "spell_equilibrium_labyrinthian",
            "sort_order": 10,
        })
    upsert(memberships, new_memberships)
    save("task_memberships.json", memberships)

    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    college = next(item for item in coverage["domains"] if item["name"] == "College of Winterhold")
    for location_id in ("windward_ruins", "north_skybound_watch", "four_skull_lookout"):
        if location_id not in college["location_ids"]:
            college["location_ids"].append(location_id)
    COVERAGE.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
