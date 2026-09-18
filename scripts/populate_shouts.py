from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src" / "skyrim_wayfinder" / "data" / "canonical"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


SHOUTS = [
    ("animal_allegiance","Animal Allegiance",("Raan","Mir","Tah"),"SKYRIM"),
    ("aura_whisper","Aura Whisper",("Laas","Yah","Nir"),"SKYRIM"),
    ("become_ethereal","Become Ethereal",("Feim","Zii","Gron"),"SKYRIM"),
    ("call_dragon","Call Dragon",("Od","Ah","Viing"),"SKYRIM"),
    ("call_of_valor","Call of Valor",("Hun","Kaal","Zoor"),"SKYRIM"),
    ("clear_skies","Clear Skies",("Lok","Vah","Koor"),"SKYRIM"),
    ("disarm","Disarm",("Zun","Haal","Viik"),"SKYRIM"),
    ("dismay","Dismay",("Faas","Ru","Maar"),"SKYRIM"),
    ("dragonrend","Dragonrend",("Joor","Zah","Frul"),"SKYRIM"),
    ("elemental_fury","Elemental Fury",("Su","Grah","Dun"),"SKYRIM"),
    ("fire_breath","Fire Breath",("Yol","Toor","Shul"),"SKYRIM"),
    ("frost_breath","Frost Breath",("Fo","Krah","Diin"),"SKYRIM"),
    ("ice_form","Ice Form",("Iiz","Slen","Nus"),"SKYRIM"),
    ("kynes_peace","Kyne's Peace",("Kaan","Drem","Ov"),"SKYRIM"),
    ("marked_for_death","Marked for Death",("Krii","Lun","Aus"),"SKYRIM"),
    ("slow_time","Slow Time",("Tiid","Klo","Ul"),"SKYRIM"),
    ("storm_call","Storm Call",("Strun","Bah","Qo"),"SKYRIM"),
    ("throw_voice","Throw Voice",("Zul","Mey","Gut"),"SKYRIM"),
    ("unrelenting_force","Unrelenting Force",("Fus","Ro","Dah"),"SKYRIM"),
    ("whirlwind_sprint","Whirlwind Sprint",("Wuld","Nah","Kest"),"SKYRIM"),
    ("drain_vitality","Drain Vitality",("Gaan","Lah","Haas"),"DAWNGUARD"),
    ("soul_tear","Soul Tear",("Rii","Vaaz","Zol"),"DAWNGUARD"),
    ("summon_durnehviir","Summon Durnehviir",("Dur","Neh","Viir"),"DAWNGUARD"),
    ("battle_fury","Battle Fury",("Mid","Vur","Shaan"),"DRAGONBORN"),
    ("bend_will","Bend Will",("Gol","Hah","Dov"),"DRAGONBORN"),
    ("cyclone","Cyclone",("Ven","Gaar","Nos"),"DRAGONBORN"),
    ("dragon_aspect","Dragon Aspect",("Mul","Qah","Diiv"),"DRAGONBORN"),
]

COLLECTION_IDS = {
    "become_ethereal":"become_ethereal", "call_dragon":"call_dragon",
    "call_of_valor":"call_of_valor", "clear_skies":"clear_skies",
    "dragonrend":"dragonrend", "fire_breath":"fire_breath",
    "storm_call":"storm_call", "unrelenting_force":"unrelenting_force",
    "whirlwind_sprint":"whirlwind_sprint",
}

WALLS = {
    "animal_allegiance":[("ancients_ascent",None),("angarvunde",None),("ysgramors_tomb","access_ysgramors_tomb")],
    "aura_whisper":[("northwind_summit",None),("valthume",None),("volunruud",None)],
    "become_ethereal":[("ironbind_barrow",None),("lost_valley_redoubt",None)],
    "disarm":[("eldersblood_peak",None),("silverdrift_lair",None),("snow_veil_sanctum","access_snow_veil_sanctum")],
    "dismay":[("dead_crone_rock",None),("lost_tongue_overlook",None),("shalidors_maze",None)],
    "elemental_fury":[("dragontooth_crater",None),("kilkreath_temple",None),("shriekwind_bastion",None)],
    "fire_breath":[("dustmans_cairn","access_dustmans_cairn"),("sunderstone_gorge",None)],
    "frost_breath":[("bonestrewn_crest",None),("folgunthur",None),("skyborn_altar",None)],
    "ice_form":[("frostmere_crypt",None),("mount_anthor",None),("saarthal","access_saarthal")],
    "kynes_peace":[("ragnvald",None),("rannveigs_fast",None),("shroud_hearth_barrow",None)],
    "marked_for_death":[("autumnwatch_tower",None),("forsaken_cave",None)],
    "slow_time":[("deepwood_redoubt",None),("korvanjund","access_korvanjund")],
    "storm_call":[("forelhost",None),("high_gate_ruins",None)],
    "whirlwind_sprint":[("dead_mens_respite","access_dead_mens_respite"),("volskygge",None)],
    "drain_vitality":[("arcwind_point",None),("dimhollow_crypt","access_dimhollow_crypt"),("forgotten_vale","access_forgotten_vale")],
    "cyclone":[("benkongerike",None),("kolbjorn_barrow","access_kolbjorn_depths"),("white_ridge_barrow",None)],
    "dragon_aspect":[("temple_of_miraak","access_temple_of_miraak"),("raven_rock_mine","access_bloodskal_barrow"),("apocrypha","access_waking_dreams")],
}

ACCESS = [
    ("access_ysgramors_tomb","Access to Ysgramor's Tomb","Reach the Companions quest stage that opens Ysgramor's Tomb.","SKYRIM","Skyrim:Glory_of_the_Dead"),
    ("access_snow_veil_sanctum","Access to Snow Veil Sanctum","Reach the Thieves Guild quest stage that opens Snow Veil Sanctum.","SKYRIM","Skyrim:Speaking_With_Silence"),
    ("access_dustmans_cairn","Access to Dustman's Cairn","Reach the Companions quest stage that opens Dustman's Cairn.","SKYRIM","Skyrim:Proving_Honor"),
    ("access_saarthal","Access to Saarthal","Reach the College quest stage that permits entry to Saarthal.","SKYRIM","Skyrim:Under_Saarthal"),
    ("access_korvanjund","Access to Korvanjund","Reach The Jagged Crown quest stage that permits entry to Korvanjund.","SKYRIM","Skyrim:The_Jagged_Crown"),
    ("access_dead_mens_respite","Access to Dead Men's Respite","Begin Tending the Flames and obtain access to Dead Men's Respite.","SKYRIM","Skyrim:Tending_the_Flames"),
    ("access_dimhollow_crypt","Access to Dimhollow Crypt","Reach the Dawnguard quest stage that opens Dimhollow Crypt.","DAWNGUARD","Skyrim:Awakening"),
    ("access_forgotten_vale","Access to the Forgotten Vale","Reach Touching the Sky and enter the Forgotten Vale.","DAWNGUARD","Skyrim:Touching_the_Sky"),
    ("access_soul_cairn","Access to the Soul Cairn and Durnehviir","Reach Beyond Death and defeat Durnehviir in the Soul Cairn.","DAWNGUARD","Skyrim:Beyond_Death"),
    ("access_vahloks_tomb","Access to Vahlok's Tomb","Begin Lost Legacy after satisfying its Solstheim prerequisites.","DRAGONBORN","Skyrim:Lost_Legacy"),
    ("access_kolbjorn_depths","Access to Kolbjorn Barrow depths","Advance Unearthed until the word wall is accessible.","DRAGONBORN","Skyrim:Unearthed"),
    ("access_bloodskal_barrow","Access through Bloodskal Barrow","Advance The Final Descent through Bloodskal Barrow.","DRAGONBORN","Skyrim:The_Final_Descent"),
    ("access_temple_of_miraak","Access to the Temple of Miraak","Advance the Dragonborn questline into the Temple of Miraak.","DRAGONBORN","Skyrim:The_Temple_of_Miraak"),
    ("access_waking_dreams","Access to Waking Dreams in Apocrypha","Reach At the Summit of Apocrypha and traverse Waking Dreams.","DRAGONBORN","Skyrim:At_the_Summit_of_Apocrypha"),
    ("access_bend_will_mind","Hermaeus Mora grants Bend Will — Mind","Reach The Gardener of Men acquisition in Apocrypha.","DRAGONBORN","Skyrim:The_Gardener_of_Men"),
    ("access_bend_will_dragon","Hermaeus Mora grants Bend Will — Dragon","Complete the Skaal knowledge exchange that grants the final word.","DRAGONBORN","Skyrim:The_Gardener_of_Men"),
]


def main():
    collections, stories, tasks = read("collections.json"), read("stories.json"), read("tasks.json")
    memberships = read("task_memberships.json")
    locations = {x["id"]: x for x in read("locations.json")}
    cids = {x["id"] for x in collections}
    sids = {x["id"] for x in stories}
    tids = {x["id"] for x in tasks}
    mids = {x["id"] for x in memberships}
    for order, (sid, name, words, source) in enumerate(SHOUTS, 10):
        cid = COLLECTION_IDS.get(sid, sid)
        COLLECTION_IDS[sid] = cid
        if cid not in cids:
            collections.append({"id":cid,"domain_id":"shouts","display_name":name,"description":f"Acquire all three words of {name}.","sort_order":order*10,"source_url":f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ','_').replace("'",'%27')}"})
            cids.add(cid)
        story_id = f"shout_{sid}_acquisitions"
        if story_id not in sids:
            stories.append({"id":story_id,"collection_id":cid,"display_name":"Word Acquisitions","sort_order":100,"source_url":f"https://en.uesp.net/wiki/Skyrim:{name.replace(' ','_').replace("'",'%27')}"})
            sids.add(story_id)

    credits = []
    def add_task(task_id, shout_id, title, location_id=None, behavior="REGIONAL_ACTION", credit=1, access=None, prereqs=None, source=None, objective=None):
        if task_id not in tids:
            task={"id":task_id,"title":title,"objective":objective or title+".","geography_type":"PHYSICAL" if location_id else "LOCATIONLESS","planner_behavior":behavior,"source_url":source or f"https://en.uesp.net/wiki/Skyrim:{SHOUTS[[x[0] for x in SHOUTS].index(shout_id)][1].replace(' ','_')}"}
            if location_id: task["location_id"]=location_id
            if access: task["access_condition_ids"]=[access]
            if prereqs: task["prerequisites"]=[{"type":"task_complete","task_id":x} for x in prereqs]
            tasks.append(task); tids.add(task_id)
        mid=f"tm_{task_id}_{shout_id}"
        if mid not in mids:
            memberships.append({"id":mid,"task_id":task_id,"story_id":f"shout_{shout_id}_acquisitions","completion_role":"REQUIRED","is_primary":True,"sort_order":len(memberships)*10})
            mids.add(mid)
        credits.append({"id":f"sc_{task_id}_{shout_id}","task_id":task_id,"shout_id":shout_id,"credit_count":credit})

    for shout_id, walls in WALLS.items():
        name=next(x[1] for x in SHOUTS if x[0]==shout_id)
        for loc, access in walls:
            add_task(f"shout_{shout_id}_{loc}",shout_id,f"Learn a word of {name} at {locations[loc]['display_name']}",loc,access=access)

    # Fixed and unusual new acquisitions.
    add_task("shout_throw_voice_shearpoint","throw_voice","Learn Throw Voice at Shearpoint","shearpoint",credit=3)
    add_task("shout_marked_for_death_sanctuary","marked_for_death","Learn a word of Marked for Death in the Dark Brotherhood Sanctuary","dark_brotherhood_sanctuary")
    sanctuary = next(item for item in tasks if item["id"] == "shout_marked_for_death_sanctuary")
    sanctuary.pop("prerequisites", None)
    sanctuary["any_of_task_ids"] = ["db_join_at_shack", "db_destroy_at_shack"]
    add_task("shout_slow_time_labyrinthian","slow_time","Learn a word of Slow Time in Labyrinthian","labyrinthian",prereqs=["college_containment_report_college"])
    add_task("shout_summon_durnehviir_soul_cairn","summon_durnehviir","Receive Summon Durnehviir in the Soul Cairn","soul_cairn",credit=3,access="access_soul_cairn")
    prior="shout_summon_durnehviir_soul_cairn"
    for index in range(1,4):
        task_id=f"shout_soul_tear_summon_{index}"
        add_task(task_id,"soul_tear",f"Summon Durnehviir in Tamriel — teaching {index}",behavior="GLOBAL_ACTION",prereqs=[prior],objective="Summon Durnehviir outdoors in Tamriel and receive the next word of Soul Tear.")
        prior=task_id
    prior=None
    for index in range(1,4):
        task_id=f"shout_battle_fury_vahloks_tomb_{index}"
        add_task(task_id,"battle_fury",f"Learn Battle Fury word {index} in Vahlok's Tomb","vahloks_tomb",access="access_vahloks_tomb",prereqs=[prior] if prior else None)
        prior=task_id
    add_task("shout_bend_will_saerings_watch","bend_will","Learn a word of Bend Will at Saering's Watch","saerings_watch")
    add_task("shout_bend_will_apocrypha","bend_will","Receive the next word of Bend Will in Apocrypha","apocrypha",access="access_bend_will_mind")
    add_task("shout_bend_will_skaal","bend_will","Receive the final word of Bend Will at Skaal Village","skaal_village",access="access_bend_will_dragon",prereqs=["shout_bend_will_apocrypha"])

    # Existing canonical acquisition Tasks.
    existing = [
        ("shout_unrelenting_force_bleak_falls","unrelenting_force",1),
        ("mq_way_voice_high_hrothgar","unrelenting_force",1),
        ("mq_horn_return_greybeards","unrelenting_force",1),
        ("mq_way_voice_whirlwind","whirlwind_sprint",1),
        ("shout_become_ethereal_ustengrav","become_ethereal",1),
        ("mq_throat_clear_skies","clear_skies",3),
        ("mq_throat_meet_paarthurnax","fire_breath",1),
        ("mq_alduins_bane_learn_dragonrend","dragonrend",3),
        ("shout_storm_call_skuldafn","storm_call",1),
        ("mq_dragonslayer_call_valor","call_of_valor",3),
    ]
    for task_id, shout_id, count in existing:
        credits.append({"id":f"sc_{task_id}_{shout_id}","task_id":task_id,"shout_id":shout_id,"credit_count":count})
    # Dah lacked its Shout membership.
    memberships.append({"id":"tm_shout_unrelenting_horn","task_id":"mq_horn_return_greybeards","story_id":"shout_unrelenting_greybeards","completion_role":"REQUIRED","is_primary":False,"sort_order":20})
    # Call Dragon belongs to the completed adviser route, never the later capture.
    memberships[:] = [m for m in memberships if m["id"] != "tm_shout_call_dragon"]
    for index, task_id in enumerate(("mq_fallen_plan_paarthurnax","mq_fallen_plan_arngeir","mq_fallen_plan_esbern"),1):
        memberships.append({"id":f"tm_shout_call_dragon_{index}","task_id":task_id,"story_id":"shout_call_dragon_fallen","completion_role":"REQUIRED","is_primary":False,"sort_order":index*10})
        credits.append({"id":f"sc_{task_id}_call_dragon","task_id":task_id,"shout_id":"call_dragon","credit_count":3})
    for task in tasks:
        if task["id"]=="shout_become_ethereal_ustengrav":
            task["prerequisites"]=[{"type":"task_complete","task_id":"mq_way_voice_whirlwind"}]

    write("collections.json",collections); write("stories.json",stories); write("tasks.json",tasks)
    write("task_memberships.json",memberships)
    write("access_conditions.json",[{"id":i,"label":l,"description":d,"source_urls":["https://en.uesp.net/wiki/"+u],"content_source":s} for i,l,d,s,u in ACCESS])
    write("shouts.json",[{"id":i,"collection_id":COLLECTION_IDS[i],"display_name":n,"words":list(w),"content_source":s,"source_url":f"https://en.uesp.net/wiki/Skyrim:{n.replace(' ','_').replace("'",'%27')}"} for i,n,w,s in SHOUTS])
    write("shout_credits.json",credits)


if __name__ == "__main__": main()
