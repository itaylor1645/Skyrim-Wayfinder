# Representative prerequisite audit

Scope: the 38 representative Increment 1 tasks only. This is not a bulk Skyrim content audit. The audit checked premature planner surfacing, return/report steps, objectives spanning locations, minimum-level gates, branch prerequisites, and special-destination access.

## Corrections made

| Task | Prerequisite before audit | Corrected prerequisite | Reason / source | Changed |
|---|---|---|---|---|
| `db_innocence_lost_speak_aventus` | Task absent | None; this is the explicit quest-start step | Aventus gives the objective before Grelod is the recommended target. [UESP: Innocence Lost](https://en.uesp.net/wiki/Skyrim:Innocence_Lost) | Yes |
| `db_innocence_lost_kill_grelod` | None | `db_innocence_lost_speak_aventus` | Prevents Riften work from surfacing before the Windhelm quest-start step. Same source as above. | Yes |
| `db_trigger_abduction_sleep` | Task absent | `db_innocence_lost_report_aventus` | Sleeping after completing Innocence Lost triggers the shack sequence. [UESP: With Friends Like These...](https://en.uesp.net/wiki/Skyrim:With_Friends_Like_These...) | Yes |
| `db_join_at_shack` / `db_destroy_at_shack` | `db_innocence_lost_report_aventus` | `db_trigger_abduction_sleep` | The choices occur only after the abduction and waking in the shack. Same source as above. | Yes |
| `college_gain_admission` | Task absent | None; this is the explicit admission step | Faralda's admission sequence precedes Tolfdir's lesson. [UESP: First Lessons](https://en.uesp.net/wiki/Skyrim:First_Lessons) | Yes |
| `college_first_lessons` | None | `college_gain_admission` | Prevents the lesson from surfacing before College admission. Same source as above. | Yes |
| `riften_stoking_flames_start` | Task absent | None; this is the explicit conversation with Balimund | Balimund requests the Fire Salts before delivery is relevant. [UESP: Stoking the Flames](https://en.uesp.net/wiki/Skyrim:Stoking_the_Flames) | Yes |
| `riften_deliver_fire_salts` | Preparation only | `riften_stoking_flames_start` plus `prep_riften_fire_salts` | Requires both receiving the request and gathering the items. Same source as above. | Yes |
| `hold_whiterun_thane` | `mq_dragon_rising_watchtower` | Unchanged prerequisite; title/objective now explicitly include reporting to Jarl Balgruuf | The return/report step was present but insufficiently visible in the task wording. [UESP: Dragon Rising](https://en.uesp.net/wiki/Skyrim:Dragon_Rising) | Wording |
| `house_breezehome_purchase` | `mq_dragon_rising_watchtower` | `hold_whiterun_thane` | Prevents the purchase from surfacing before the Dragon Rising return/report step. [UESP: Breezehome](https://en.uesp.net/wiki/Skyrim:Breezehome) | Yes |
| `mq_way_voice_high_hrothgar` | `mq_dragon_rising_watchtower` | `hold_whiterun_thane` | Prevents High Hrothgar from surfacing before Dragon Rising is reported and the Greybeards' summons is handled. [UESP: The Way of the Voice](https://en.uesp.net/wiki/Skyrim:The_Way_of_the_Voice) | Yes |

## Verified without prerequisite changes

| Tasks | Current prerequisite chain | Audit result / source context | Changed |
|---|---|---|---|
| `mq_unbound_escape_helgen` through `mq_dragon_rising_watchtower` | Helgen → Riverwood → Whiterun → accept/recover/return Dragonstone → Western Watchtower | Physical legs and return step remain atomic; representative main-quest ordering is internally consistent. Canonical task/Story sources apply. | No |
| `collectible_golden_claw_recover`, `golden_claw_return_lucan` | Acquire claw; returning it requires acquisition | The collectible is satisfied on acquisition while the Side Quest continues to Lucan, as approved. | No |
| `shout_unrelenting_force_bleak_falls` | None | Deliberately available at the shared dungeon location; no unsupported quest dependency added. | No |
| `college_under_saarthal` through `college_staff_magnus`; `mask_morokei` | First Lessons → Saarthal → Fellglow → College → Mzulft → College report → Winterhold defense → College report → Labyrinthian | Location changes have explicit return/report tasks where represented. Labyrinthian remains locked until its College report prerequisite. Canonical task/Story sources apply. | No |
| `prep_riften_fire_salts` | None | Preparation is intentionally collectible before the quest starts; it does not unlock delivery by itself. | No |
| `db_innocence_lost_report_aventus` | Kill Grelod | Explicit Windhelm report leg remains correctly gated. | No |
| `mq_the_fallen_milestone` | `mq_way_voice_high_hrothgar` | Retained as a non-recommended manual bookkeeping bridge because omitted main-quest content cannot safely be inferred. Its label states the actual completion condition. | No |
| `mq_skuldafn_reach_portal`, `mask_nahkriin`, `shout_storm_call_skuldafn` | `mq_the_fallen_milestone` | Special-destination work remains hidden until an actionable objective unlocks. Skuldafn keeps one-way/missable metadata and now exposes Dragonsreach as departure. | No |
| `daedric_break_of_dawn_beacon` | Minimum level 12 | Level gate retained; OPPORTUNISTIC behavior prevents an artificial regional recommendation for the randomized discovery. [UESP: The Break of Dawn](https://en.uesp.net/wiki/Skyrim:The_Break_of_Dawn) | No |

## Migration behavior

Schema version 3 infers each newly explicit prerequisite step as Complete only when downstream prototype state proves it happened. Existing states on the kill/report, College lesson, Fire Salts delivery, and Dark Brotherhood branch tasks remain unchanged. Otherwise the new tasks use normal automatic evaluation.
