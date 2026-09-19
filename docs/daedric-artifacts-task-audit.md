# Daedric Artifacts Task Audit

Generated from the canonical dataset. Do not edit by hand.

- Standalone Daedric quest Stories: 15
- Skeleton Key acquisition bridges: 1
- Artifact identities: 19
- Oblivion Walker-eligible identities: 17
- Canonical Tasks represented: 88
- Reused Tasks: 5
- Newly authored Tasks: 83
- Approved geography additions: 5
- Branching choice sets: 7

## Quest and task matrix

### The Black Star — Azura

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_black_star_visit_shrine` — Consult Aranea at the Shrine of Azura | REGIONAL_ACTION | Shrine of Azura / Winterhold | None | — |
| `daedric_black_star_consult_nelacar` — Consult Nelacar | REGIONAL_ACTION | The Frozen Hearth / Winterhold | `daedric_black_star_visit_shrine` | — |
| `daedric_black_star_recover_broken` — Recover the Broken Star | REGIONAL_ACTION | Ilinalta's Deep / Falkreath | `daedric_black_star_consult_nelacar` | — |
| `artifact_azuras_star_acquire` — Restore Azura's Star | REGIONAL_ACTION | Shrine of Azura / Winterhold | `daedric_black_star_recover_broken` | `daedric_azura_reward` → `azura` |
| `artifact_black_star_acquire` — Create the Black Star | REGIONAL_ACTION | The Frozen Hearth / Winterhold | `daedric_black_star_recover_broken` | `daedric_azura_reward` → `black` |

Artifacts: **Azura's Star** (eligible for Oblivion Walker; credit `artifact_azuras_star_acquire`), **The Black Star** (eligible for Oblivion Walker; credit `artifact_black_star_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Black_Star

### Boethiah's Calling — Boethiah

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_boethiah_reach_sacellum` — Meet Boethiah's cult | REGIONAL_ACTION | Sacellum of Boethiah / Windhelm | Level 30 | — |
| `daedric_boethiah_sacrifice_follower` — Complete Boethiah's sacrifice | REGIONAL_ACTION | Sacellum of Boethiah / Windhelm | `daedric_boethiah_reach_sacellum` | — |
| `artifact_ebony_mail_acquire` — Acquire the Ebony Mail | REGIONAL_ACTION | Knifepoint Ridge / Falkreath | `daedric_boethiah_sacrifice_follower` | — |

Artifacts: **Ebony Mail** (eligible for Oblivion Walker; credit `artifact_ebony_mail_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:Boethiah%27s_Calling

### A Daedra's Best Friend — Clavicus Vile

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_best_friend_speak_lod` — Ask Lod about the stray dog | REGIONAL_ACTION | Falkreath / Falkreath | Level 10 | — |
| `daedric_best_friend_meet_barbas` — Meet Barbas | REGIONAL_ACTION | Falkreath / Falkreath | `daedric_best_friend_speak_lod` | — |
| `daedric_best_friend_find_shrine` — Reach Clavicus Vile's shrine | REGIONAL_ACTION | Haemar's Shame / Falkreath | `daedric_best_friend_meet_barbas` | — |
| `daedric_best_friend_recover_axe` — Recover the Rueful Axe | REGIONAL_ACTION | Rimerock Burrow / Solitude | `daedric_best_friend_find_shrine` | — |
| `artifact_masque_clavicus_acquire` — Return the Axe and acquire the Masque | REGIONAL_ACTION | Haemar's Shame / Falkreath | `daedric_best_friend_recover_axe` | `daedric_clavicus_reward` → `masque` |
| `artifact_rueful_axe_acquire` — Kill Barbas and keep the Rueful Axe | REGIONAL_ACTION | Haemar's Shame / Falkreath | `daedric_best_friend_recover_axe` | `daedric_clavicus_reward` → `axe` |

Artifacts: **The Rueful Axe** (not eligible for Oblivion Walker; credit `artifact_rueful_axe_acquire`), **Masque of Clavicus Vile** (eligible for Oblivion Walker; credit `artifact_masque_clavicus_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:A_Daedra%27s_Best_Friend

### Discerning the Transmundane — Hermaeus Mora

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `mq_elder_consult_septimus` — Consult Septimus Signus | REGIONAL_ACTION | Septimus Signus's Outpost / Winterhold | any: `mq_throat_meet_paarthurnax`<br>any: `daedric_discerning_seek_septimus` | — |
| `mq_elder_descend_alftand` — Descend through Alftand | REGIONAL_ACTION | Alftand / Winterhold | `mq_elder_consult_septimus` | — |
| `mq_elder_cross_blackreach` — Cross Blackreach to the Tower of Mzark | REGIONAL_ACTION | Blackreach / Blackreach | `mq_elder_descend_alftand` | — |
| `mq_elder_acquire_scroll` — Acquire the Elder Scroll (Dragon) | REGIONAL_ACTION | Tower of Mzark / Blackreach | `mq_elder_cross_blackreach` | — |
| `daedric_discerning_seek_septimus` — Ask Septimus about the Dwemer lockbox | REGIONAL_ACTION | Septimus Signus's Outpost / Winterhold | None | — |
| `daedric_discerning_return_lexicon` — Return the transcribed Lexicon | REGIONAL_ACTION | Septimus Signus's Outpost / Winterhold | `mq_elder_acquire_scroll` | — |
| `daedric_discerning_resume_research` — Resume Septimus's research | REGIONAL_ACTION | Septimus Signus's Outpost / Winterhold | Level 15<br>`daedric_discerning_return_lexicon` | — |
| `daedric_discerning_harvest_blood` — Harvest blood from the five elven races | OPPORTUNISTIC | No fixed location | `daedric_discerning_resume_research` | — |
| `daedric_discerning_deliver_blood` — Deliver the blood samples | REGIONAL_ACTION | Septimus Signus's Outpost / Winterhold | `daedric_discerning_harvest_blood` | — |
| `artifact_oghma_infinium_acquire` — Acquire the Oghma Infinium | REGIONAL_ACTION | Septimus Signus's Outpost / Winterhold | `daedric_discerning_deliver_blood` | — |

Artifacts: **Oghma Infinium** (eligible for Oblivion Walker; credit `artifact_oghma_infinium_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:Discerning_the_Transmundane

### Ill Met by Moonlight — Hircine

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_ill_met_speak_sinding` — Speak with Sinding | REGIONAL_ACTION | Falkreath Jail / Falkreath | None | — |
| `daedric_ill_met_hunt_stag` — Hunt Hircine's White Stag | OPPORTUNISTIC | No fixed location | `daedric_ill_met_speak_sinding` | — |
| `artifact_ring_hircine_acquire` — Spare Sinding and acquire the Ring of Hircine | REGIONAL_ACTION | Bloated Man's Grotto / Falkreath | `daedric_ill_met_hunt_stag` | `daedric_hircine_reward` → `ring` |
| `artifact_saviors_hide_acquire` — Kill Sinding and acquire Savior's Hide | REGIONAL_ACTION | Bloated Man's Grotto / Falkreath | `daedric_ill_met_hunt_stag` | `daedric_hircine_reward` → `hide` |

Artifacts: **Ring of Hircine** (eligible for Oblivion Walker; credit `artifact_ring_hircine_acquire`), **Savior's Hide** (eligible for Oblivion Walker; credit `artifact_saviors_hide_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:Ill_Met_By_Moonlight

### The Cursed Tribe — Malacath

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `prep_cursed_tribe_ingredients` — Set aside troll fat and a Daedra heart | PREPARATION | No fixed location | `daedric_cursed_defend_largashbur` | — |
| `daedric_cursed_defend_largashbur` — Defend Largashbur | REGIONAL_ACTION | Largashbur / Riften | Level 9 | — |
| `daedric_cursed_complete_ritual` — Complete Atub's ritual | REGIONAL_ACTION | Largashbur / Riften | `prep_cursed_tribe_ingredients` | — |
| `daedric_cursed_defeat_giant` — Defeat the giant in Giant's Grove | REGIONAL_ACTION | Fallowstone Cave / Riften | `daedric_cursed_complete_ritual` | — |
| `daedric_cursed_place_hammer` — Place Shagrol's Warhammer on the shrine | REGIONAL_ACTION | Largashbur / Riften | `daedric_cursed_defeat_giant` | — |
| `artifact_volendrung_acquire` — Take Volendrung | REGIONAL_ACTION | Largashbur / Riften | `daedric_cursed_place_hammer` | — |

Artifacts: **Volendrung** (eligible for Oblivion Walker; credit `artifact_volendrung_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Cursed_Tribe

### Pieces of the Past — Mehrunes Dagon

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_pieces_visit_museum` — Visit the Mythic Dawn Museum | REGIONAL_ACTION | Mythic Dawn Museum / Dawnstar | Level 20 | — |
| `daedric_pieces_recover_pommel` — Recover the Razor's pommel | REGIONAL_ACTION | Dead Crone Rock / Markarth | `daedric_pieces_visit_museum` | — |
| `daedric_pieces_recover_shards` — Recover the Razor's blade shards | REGIONAL_ACTION | Cracked Tusk Keep / Falkreath | `daedric_pieces_visit_museum` | — |
| `daedric_pieces_recover_hilt` — Recover the Razor's hilt | REGIONAL_ACTION | Jorgen and Lami's House / Morthal | `daedric_pieces_visit_museum` | — |
| `daedric_pieces_return_fragments` — Return the Razor fragments | REGIONAL_ACTION | Mythic Dawn Museum / Dawnstar | `daedric_pieces_recover_pommel`<br>`daedric_pieces_recover_shards`<br>`daedric_pieces_recover_hilt` | — |
| `artifact_mehrunes_razor_acquire` — Kill Silus and acquire Mehrunes' Razor | REGIONAL_ACTION | Shrine of Mehrunes Dagon / Dawnstar | `daedric_pieces_return_fragments` | `daedric_razor_fate` → `razor` |
| `daedric_pieces_spare_silus` — Spare Silus | REGIONAL_ACTION | Shrine of Mehrunes Dagon / Dawnstar | `daedric_pieces_return_fragments` | `daedric_razor_fate` → `spared` |

Artifacts: **Mehrunes' Razor** (eligible for Oblivion Walker; credit `artifact_mehrunes_razor_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:Pieces_of_the_Past

### The Whispering Door — Mephala

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_whisper_hear_rumor` — Ask about Balgruuf's strange children | REGIONAL_ACTION | Whiterun / Whiterun | Level 20<br>`hold_whiterun_thane` | — |
| `daedric_whisper_investigate_door` — Investigate the Whispering Door | REGIONAL_ACTION | Dragonsreach / Whiterun | `daedric_whisper_hear_rumor` | — |
| `artifact_ebony_blade_acquire` — Acquire the Ebony Blade | REGIONAL_ACTION | Dragonsreach / Whiterun | `daedric_whisper_investigate_door` | — |

Artifacts: **Ebony Blade** (eligible for Oblivion Walker; credit `artifact_ebony_blade_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Whispering_Door

### The Break of Dawn — Meridia

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_break_of_dawn_beacon` — Find Meridia's Beacon | OPPORTUNISTIC | No fixed location | Level 12 | — |
| `daedric_break_return_beacon` — Return Meridia's Beacon | REGIONAL_ACTION | Kilkreath Temple / Solitude | `daedric_break_of_dawn_beacon` | — |
| `artifact_dawnbreaker_acquire` — Acquire Dawnbreaker | REGIONAL_ACTION | Kilkreath Temple / Solitude | `daedric_break_return_beacon` | — |

Artifacts: **Dawnbreaker** (eligible for Oblivion Walker; credit `artifact_dawnbreaker_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Break_of_Dawn

### The House of Horrors — Molag Bal

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_house_enter_abandoned` — Enter the Abandoned House with Tyranus | REGIONAL_ACTION | Abandoned House / Markarth | access: `access_forsworn_conspiracy_started` | — |
| `daedric_house_record_logrolf_location` — Record Logrolf's assigned prison | MILESTONE | No fixed location | `daedric_house_enter_abandoned` | observed outcome: broken_tower, brucas_leap, deepwood, druadach, hag_rock, red_eagle |
| `daedric_house_free_logrolf_broken_tower` — Free Logrolf at Broken Tower Redoubt | REGIONAL_ACTION | Broken Tower Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `freed` |
| `daedric_house_kill_logrolf_broken_tower` — Kill captive Logrolf at Broken Tower Redoubt | REGIONAL_ACTION | Broken Tower Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `killed` |
| `daedric_house_free_logrolf_brucas_leap` — Free Logrolf at Bruca's Leap Redoubt | REGIONAL_ACTION | Bruca's Leap Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `freed` |
| `daedric_house_kill_logrolf_brucas_leap` — Kill captive Logrolf at Bruca's Leap Redoubt | REGIONAL_ACTION | Bruca's Leap Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `killed` |
| `daedric_house_free_logrolf_deepwood` — Free Logrolf at Deepwood Redoubt | REGIONAL_ACTION | Deepwood Redoubt / Hag's End / Solitude | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `freed` |
| `daedric_house_kill_logrolf_deepwood` — Kill captive Logrolf at Deepwood Redoubt | REGIONAL_ACTION | Deepwood Redoubt / Hag's End / Solitude | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `killed` |
| `daedric_house_free_logrolf_druadach` — Free Logrolf at Druadach Redoubt | REGIONAL_ACTION | Druadach Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `freed` |
| `daedric_house_kill_logrolf_druadach` — Kill captive Logrolf at Druadach Redoubt | REGIONAL_ACTION | Druadach Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `killed` |
| `daedric_house_free_logrolf_hag_rock` — Free Logrolf at Hag Rock Redoubt | REGIONAL_ACTION | Hag Rock Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `freed` |
| `daedric_house_kill_logrolf_hag_rock` — Kill captive Logrolf at Hag Rock Redoubt | REGIONAL_ACTION | Hag Rock Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `killed` |
| `daedric_house_free_logrolf_red_eagle` — Free Logrolf at Red Eagle Redoubt | REGIONAL_ACTION | Red Eagle Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `freed` |
| `daedric_house_kill_logrolf_red_eagle` — Kill captive Logrolf at Red Eagle Redoubt | REGIONAL_ACTION | Red Eagle Redoubt / Markarth | `daedric_house_record_logrolf_location` | `daedric_logrolf_fate` → `killed` |
| `artifact_mace_molag_bal_acquire` — Acquire the Mace of Molag Bal | REGIONAL_ACTION | Abandoned House / Markarth | any: `daedric_house_free_logrolf_broken_tower`<br>any: `daedric_house_free_logrolf_brucas_leap`<br>any: `daedric_house_free_logrolf_deepwood`<br>any: `daedric_house_free_logrolf_druadach`<br>any: `daedric_house_free_logrolf_hag_rock`<br>any: `daedric_house_free_logrolf_red_eagle` | `daedric_logrolf_fate` → `freed` |

Artifacts: **Mace of Molag Bal** (eligible for Oblivion Walker; credit `artifact_mace_molag_bal_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_House_of_Horrors

### The Taste of Death — Namira

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_taste_investigate_hall` — Investigate Markarth's Hall of the Dead | REGIONAL_ACTION | Markarth Hall of the Dead / Markarth | None | — |
| `daedric_taste_clear_reachcliff` — Clear Reachcliff Cave | REGIONAL_ACTION | Reachcliff Cave / Markarth | `daedric_taste_investigate_hall` | — |
| `daedric_taste_lure_verulus` — Bring Verulus to Reachcliff Cave | REGIONAL_ACTION | Markarth Hall of the Dead / Markarth | `daedric_taste_clear_reachcliff` | — |
| `artifact_ring_namira_acquire` — Complete the feast and acquire the Ring of Namira | REGIONAL_ACTION | Reachcliff Cave / Markarth | `daedric_taste_lure_verulus` | `daedric_namira_fate` → `ring` |
| `daedric_taste_save_verulus` — Kill Eola and save Verulus | REGIONAL_ACTION | Reachcliff Cave / Markarth | `daedric_taste_lure_verulus` | `daedric_namira_fate` → `saved` |

Artifacts: **Ring of Namira** (eligible for Oblivion Walker; credit `artifact_ring_namira_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Taste_of_Death

### The Only Cure — Peryite

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `prep_only_cure_ingredients` — Set aside Kesh's incense ingredients | PREPARATION | No fixed location | `daedric_only_cure_meet_kesh` | — |
| `daedric_only_cure_meet_kesh` — Meet Kesh at the Shrine to Peryite | REGIONAL_ACTION | Shrine to Peryite / Markarth | Level 12 | — |
| `daedric_only_cure_inhale_incense` — Commune with Peryite | REGIONAL_ACTION | Shrine to Peryite / Markarth | `prep_only_cure_ingredients` | — |
| `daedric_only_cure_kill_orchendor` — Kill Orchendor | REGIONAL_ACTION | Bthardamz / Markarth | `daedric_only_cure_inhale_incense` | — |
| `artifact_spellbreaker_acquire` — Acquire Spellbreaker | REGIONAL_ACTION | Shrine to Peryite / Markarth | `daedric_only_cure_kill_orchendor` | — |

Artifacts: **Spellbreaker** (eligible for Oblivion Walker; credit `artifact_spellbreaker_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Only_Cure

### A Night to Remember — Sanguine

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_night_meet_sam` — Meet Sam Guevenne | OPPORTUNISTIC | No fixed location | Level 14 | — |
| `daedric_night_temple_dibella` — Investigate the Temple of Dibella | REGIONAL_ACTION | Temple of Dibella / Markarth | `daedric_night_meet_sam` | — |
| `daedric_night_visit_rorikstead` — Investigate Rorikstead | REGIONAL_ACTION | Rorikstead / Whiterun | `daedric_night_temple_dibella` | — |
| `daedric_night_speak_ysolda` — Ask Ysolda about the wedding | REGIONAL_ACTION | Whiterun / Whiterun | `daedric_night_visit_rorikstead` | observed outcome: resolved, retrieve_ring |
| `daedric_night_retrieve_ring` — Retrieve the wedding ring | REGIONAL_ACTION | Witchmist Grove / Windhelm | `daedric_night_speak_ysolda` | when `daedric_night_speak_ysolda` = `retrieve_ring` |
| `daedric_night_return_ring` — Return the wedding ring to Ysolda | REGIONAL_ACTION | Whiterun / Whiterun | `daedric_night_retrieve_ring` | when `daedric_night_speak_ysolda` = `retrieve_ring` |
| `daedric_night_reach_portal` — Find Sam's portal | REGIONAL_ACTION | Morvunskar / Windhelm | `daedric_night_speak_ysolda`<br>`daedric_night_return_ring` | — |
| `artifact_sanguine_rose_acquire` — Acquire the Sanguine Rose | REGIONAL_ACTION | Misty Grove / Misty Grove | `daedric_night_reach_portal` | — |

Artifacts: **Sanguine Rose** (eligible for Oblivion Walker; credit `artifact_sanguine_rose_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:A_Night_To_Remember

### The Mind of Madness — Sheogorath

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_mind_speak_dervenin` — Speak with Dervenin | REGIONAL_ACTION | Solitude / Solitude | None | — |
| `daedric_mind_enter_pelagius_wing` — Enter the Pelagius Wing | REGIONAL_ACTION | Blue Palace / Solitude | `daedric_mind_speak_dervenin` | — |
| `artifact_wabbajack_acquire` — Complete Pelagius's trials and acquire Wabbajack | REGIONAL_ACTION | Blue Palace / Solitude | `daedric_mind_enter_pelagius_wing` | — |

Artifacts: **Wabbajack** (eligible for Oblivion Walker; credit `artifact_wabbajack_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:The_Mind_of_Madness

### Waking Nightmare — Vaermina

| Task | Behavior | Location / Region | Prerequisites and access | Branch / outcome |
|---|---|---|---|---|
| `daedric_waking_follow_erandur` — Follow Erandur to Nightcaller Temple | REGIONAL_ACTION | Windpeak Inn / Dawnstar | None | — |
| `daedric_waking_reach_skull` — Reach the Skull of Corruption | REGIONAL_ACTION | Nightcaller Temple / Dawnstar | `daedric_waking_follow_erandur` | — |
| `artifact_skull_corruption_acquire` — Kill Erandur and acquire the Skull of Corruption | REGIONAL_ACTION | Nightcaller Temple / Dawnstar | `daedric_waking_reach_skull` | `daedric_vaermina_fate` → `skull` |
| `daedric_waking_destroy_skull` — Allow Erandur to destroy the Skull | REGIONAL_ACTION | Nightcaller Temple / Dawnstar | `daedric_waking_reach_skull` | `daedric_vaermina_fate` → `destroyed` |

Artifacts: **Skull of Corruption** (eligible for Oblivion Walker; credit `artifact_skull_corruption_acquire`)

Source: https://en.uesp.net/wiki/Skyrim:Waking_Nightmare

## Skeleton Key acquisition bridge

The Skeleton Key is tracked through `artifact_skeleton_key_acquire` at Irkngthand, gated by `access_blindsighted_irkngthand`. The same historical acquisition Task is a REQUIRED secondary membership of Blindsighted; returning the Key in Darkness Returns is a separate faction event and does not undo its collectible credit.

Oblivion Walker eligible: **no**.

## Artifact catalog vs Oblivion Walker

Wayfinder tracks 19 historically acquired artifact identities. Oblivion Walker recognizes 17 of those identities and requires 15 qualifying acquisitions. The Rueful Axe and Skeleton Key remain valid Wayfinder collectibles but are explicitly ineligible. Azura's two rewards and Hircine's two rewards each qualify individually, while Wayfinder models their intended normal routes as mutually exclusive and does not model exploit-based double rewards.

Quest completion and artifact acquisition are separate. In particular, The Cursed Tribe completes when Shagrol's Warhammer is placed, while `artifact_volendrung_acquire` records physically taking Volendrung afterward.

The collection service reports acquired, currently achievable, and full catalog totals separately. Irreversible recorded choices remove unavailable identities only from the achievable denominator; their catalog entries and Not Applicable reasons remain inspectable.

Primary reference: https://en.uesp.net/wiki/Skyrim:Daedric_Quests
