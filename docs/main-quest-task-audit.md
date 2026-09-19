# Main Quest canonical task audit

> Generated from the canonical dataset by `scripts/generate_main_quest_audit.py`.

## Scope summary

- Stories: **19** (including conditional and optional Stories)
- Unique Tasks represented under Main Quest: **56**
- Main Quest memberships: **56**
- Main Quest Tasks with cross-category membership: **21**
- Geography corrections made during Increment 2B: **none**

Only Tasks own geography. Every Region below is derived from `Task.location_id → Location.region_id`.

## Unbound (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Unbound](https://en.uesp.net/wiki/Skyrim:Unbound)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Escape Helgen](https://en.uesp.net/wiki/Skyrim:Unbound) (REQUIRED) | Helgen Keep → Falkreath | None | REGIONAL_ACTION | — | — |

## Before the Storm (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Before_the_Storm](https://en.uesp.net/wiki/Skyrim:Before_the_Storm)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| Reach Riverwood (ASSOCIATED) | Riverwood → Whiterun | Escape Helgen | REGIONAL_ACTION | — | — |
| Warn Jarl Balgruuf (REQUIRED) | Dragonsreach → Whiterun | Escape Helgen | REGIONAL_ACTION | — | — |

## Bleak Falls Barrow (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Bleak_Falls_Barrow_(quest)](https://en.uesp.net/wiki/Skyrim:Bleak_Falls_Barrow_(quest))

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| Speak to Farengar (REQUIRED) | Dragonsreach → Whiterun | Warn Jarl Balgruuf | REGIONAL_ACTION | — | — |
| Recover the Dragonstone (REQUIRED) | Bleak Falls Barrow → Whiterun | Speak to Farengar; Recover the Golden Claw | REGIONAL_ACTION | — | — |
| [Recover the Golden Claw](https://en.uesp.net/wiki/Skyrim:The_Golden_Claw) (ASSOCIATED) | Bleak Falls Barrow → Whiterun | None | REGIONAL_ACTION | Artifacts & Collectibles / Dragon Claws / Golden Claw (REQUIRED); Side Quests / Skyrim Side Quests / The Golden Claw (REQUIRED) | — |
| [Learn Unrelenting Force — Force](https://en.uesp.net/wiki/Skyrim:Unrelenting_Force) (ASSOCIATED) | Bleak Falls Barrow → Whiterun | None | REGIONAL_ACTION | Shouts / Unrelenting Force / Bleak Falls Barrow (REQUIRED) | — |
| Deliver the Dragonstone (REQUIRED) | Dragonsreach → Whiterun | Recover the Dragonstone | REGIONAL_ACTION | — | — |

## Dragon Rising (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Dragon_Rising](https://en.uesp.net/wiki/Skyrim:Dragon_Rising)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| Defeat the Dragon at the Western Watchtower (REQUIRED) | Western Watchtower → Whiterun | Deliver the Dragonstone | REGIONAL_ACTION | — | — |
| [Report to Jarl Balgruuf and Become Thane](https://en.uesp.net/wiki/Skyrim:Dragon_Rising) (REQUIRED) | Dragonsreach → Whiterun | Defeat the Dragon at the Western Watchtower | REGIONAL_ACTION | Holds & Homes / Whiterun / Thane of Whiterun (REQUIRED) | — |

## The Way of the Voice (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:The_Way_of_the_Voice](https://en.uesp.net/wiki/Skyrim:The_Way_of_the_Voice)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Answer the Greybeards and Learn Ro](https://en.uesp.net/wiki/Skyrim:The_Way_of_the_Voice) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Report to Jarl Balgruuf and Become Thane | REGIONAL_ACTION | Shouts / Unrelenting Force / Greybeard Training (REQUIRED) | — |
| [Learn Whirlwind Sprint](https://en.uesp.net/wiki/Skyrim:Whirlwind_Sprint) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Answer the Greybeards and Learn Ro | REGIONAL_ACTION | Shouts / Whirlwind Sprint / Greybeard Training (REQUIRED) | — |

## The Horn of Jurgen Windcaller (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:The_Horn_of_Jurgen_Windcaller](https://en.uesp.net/wiki/Skyrim:The_Horn_of_Jurgen_Windcaller)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Search Ustengrav for the Horn](https://en.uesp.net/wiki/Skyrim:The_Horn_of_Jurgen_Windcaller) (REQUIRED) | Ustengrav → Morthal | Learn Whirlwind Sprint | REGIONAL_ACTION | — | — |
| [Learn a word of Become Ethereal at Ustengrav](https://en.uesp.net/wiki/Skyrim:Become_Ethereal) (ASSOCIATED) | Ustengrav → Morthal | Learn Whirlwind Sprint | REGIONAL_ACTION | Shouts / Become Ethereal / Ustengrav (REQUIRED) | — |
| [Meet the Horn's Taker](https://en.uesp.net/wiki/Skyrim:The_Horn_of_Jurgen_Windcaller) (REQUIRED) | Sleeping Giant Inn → Whiterun | Search Ustengrav for the Horn | REGIONAL_ACTION | — | — |
| [Return the Horn and Receive Dah](https://en.uesp.net/wiki/Skyrim:The_Horn_of_Jurgen_Windcaller) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Meet the Horn's Taker | REGIONAL_ACTION | Shouts / Unrelenting Force / Greybeard Training (REQUIRED) | — |

## A Blade in the Dark (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:A_Blade_in_the_Dark](https://en.uesp.net/wiki/Skyrim:A_Blade_in_the_Dark)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Defeat Sahloknir with Delphine](https://en.uesp.net/wiki/Skyrim:A_Blade_in_the_Dark) (REQUIRED) | Kynesgrove → Windhelm | Return the Horn and Receive Dah | REGIONAL_ACTION | — | — |

## Diplomatic Immunity (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity](https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Plan the Embassy Infiltration](https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity) (REQUIRED) | Sleeping Giant Inn → Whiterun | Defeat Sahloknir with Delphine | REGIONAL_ACTION | — | — |
| [Give Equipment to Malborn](https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity) (REQUIRED) | The Winking Skeever → Solitude | Plan the Embassy Infiltration | REGIONAL_ACTION | — | — |
| [Meet Delphine and Depart for the Embassy](https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity) (REQUIRED) | Katla's Farm → Solitude | Give Equipment to Malborn | REGIONAL_ACTION | — | — |
| [Recover the Thalmor Intelligence](https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity) (REQUIRED) | Thalmor Embassy → Solitude | Meet Delphine and Depart for the Embassy | REGIONAL_ACTION | — | Missable; Full embassy access is quest-gated; finish the intelligence search before escaping. |
| [Escape the Embassy](https://en.uesp.net/wiki/Skyrim:Diplomatic_Immunity) (REQUIRED) | Reeking Cave → Solitude | Recover the Thalmor Intelligence | REGIONAL_ACTION | — | — |

## A Cornered Rat (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:A_Cornered_Rat](https://en.uesp.net/wiki/Skyrim:A_Cornered_Rat)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Find Esbern in the Ratway](https://en.uesp.net/wiki/Skyrim:A_Cornered_Rat) (REQUIRED) | The Ratway → Riften | Escape the Embassy | REGIONAL_ACTION | — | — |
| [Bring Esbern to Delphine](https://en.uesp.net/wiki/Skyrim:A_Cornered_Rat) (REQUIRED) | Sleeping Giant Inn → Whiterun | Find Esbern in the Ratway | REGIONAL_ACTION | — | — |

## Alduin's Wall (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Alduin%27s_Wall](https://en.uesp.net/wiki/Skyrim:Alduin%27s_Wall)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Reach Sky Haven Temple through Karthspire](https://en.uesp.net/wiki/Skyrim:Alduin%27s_Wall) (REQUIRED) | Karthspire → Markarth | Bring Esbern to Delphine | REGIONAL_ACTION | — | — |
| [Open Sky Haven Temple and Study Alduin's Wall](https://en.uesp.net/wiki/Skyrim:Alduin%27s_Wall) (REQUIRED) | Sky Haven Temple → Markarth | Reach Sky Haven Temple through Karthspire | REGIONAL_ACTION | — | — |

## The Throat of the World (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:The_Throat_of_the_World](https://en.uesp.net/wiki/Skyrim:The_Throat_of_the_World)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Receive Clear Skies](https://en.uesp.net/wiki/Skyrim:Clear_Skies) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Open Sky Haven Temple and Study Alduin's Wall | REGIONAL_ACTION | Shouts / Clear Skies / High Hrothgar (REQUIRED) | — |
| [Meet Paarthurnax and Learn Fire Breath](https://en.uesp.net/wiki/Skyrim:The_Throat_of_the_World) (REQUIRED) | Throat of the World → High Hrothgar / Throat of the World | Receive Clear Skies | REGIONAL_ACTION | Shouts / Fire Breath / Throat of the World (REQUIRED) | — |

## Elder Knowledge (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Elder_Knowledge](https://en.uesp.net/wiki/Skyrim:Elder_Knowledge)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Consult Septimus Signus](https://en.uesp.net/wiki/Skyrim:Elder_Knowledge) (REQUIRED) | Septimus Signus's Outpost → Winterhold | Any one: Meet Paarthurnax and Learn Fire Breath / Ask Septimus about the Dwemer lockbox | REGIONAL_ACTION | Artifacts & Collectibles / Daedric Artifacts / Discerning the Transmundane (REQUIRED) | — |
| [Descend through Alftand](https://en.uesp.net/wiki/Skyrim:Elder_Knowledge) (REQUIRED) | Alftand → Winterhold | Consult Septimus Signus | REGIONAL_ACTION | Artifacts & Collectibles / Daedric Artifacts / Discerning the Transmundane (REQUIRED) | — |
| [Cross Blackreach to the Tower of Mzark](https://en.uesp.net/wiki/Skyrim:Elder_Knowledge) (REQUIRED) | Blackreach → Blackreach | Descend through Alftand | REGIONAL_ACTION | Artifacts & Collectibles / Daedric Artifacts / Discerning the Transmundane (REQUIRED) | — |
| [Acquire the Elder Scroll (Dragon)](https://en.uesp.net/wiki/Skyrim:Elder_Knowledge) (REQUIRED) | Tower of Mzark → Blackreach | Cross Blackreach to the Tower of Mzark | REGIONAL_ACTION | Artifacts & Collectibles / Daedric Artifacts / Discerning the Transmundane (REQUIRED) | — |

## Alduin's Bane (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Alduin%27s_Bane](https://en.uesp.net/wiki/Skyrim:Alduin%27s_Bane)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Learn Dragonrend from the Elder Scroll](https://en.uesp.net/wiki/Skyrim:Alduin%27s_Bane) (REQUIRED) | Throat of the World → High Hrothgar / Throat of the World | Acquire the Elder Scroll (Dragon) | REGIONAL_ACTION | Shouts / Dragonrend / Throat of the World (REQUIRED) | — |
| [Drive Alduin from the Throat of the World](https://en.uesp.net/wiki/Skyrim:Alduin%27s_Bane) (REQUIRED) | Throat of the World → High Hrothgar / Throat of the World | Learn Dragonrend from the Elder Scroll | REGIONAL_ACTION | — | — |

## The Fallen (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:The_Fallen](https://en.uesp.net/wiki/Skyrim:The_Fallen)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Learn the Trapping Plan from Paarthurnax](https://en.uesp.net/wiki/Skyrim:The_Fallen) (REQUIRED) | Throat of the World → High Hrothgar / Throat of the World | Drive Alduin from the Throat of the World | REGIONAL_ACTION | Shouts / Call Dragon / The Fallen (REQUIRED) | — |
| [Learn the Trapping Plan from Arngeir](https://en.uesp.net/wiki/Skyrim:The_Fallen) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Drive Alduin from the Throat of the World | REGIONAL_ACTION | Shouts / Call Dragon / The Fallen (REQUIRED) | — |
| [Learn the Trapping Plan from Esbern](https://en.uesp.net/wiki/Skyrim:The_Fallen) (REQUIRED) | Sky Haven Temple → Markarth | Drive Alduin from the Throat of the World | REGIONAL_ACTION | Shouts / Call Dragon / The Fallen (REQUIRED) | — |
| [Ask the Jarl to Use Dragonsreach](https://en.uesp.net/wiki/Skyrim:The_Fallen) (REQUIRED) | Dragonsreach → Whiterun | Any one: Learn the Trapping Plan from Paarthurnax / Learn the Trapping Plan from Arngeir / Learn the Trapping Plan from Esbern | REGIONAL_ACTION | — | — |
| [Capture and Interrogate Odahviing](https://en.uesp.net/wiki/Skyrim:The_Fallen) (REQUIRED) | Dragonsreach → Whiterun | Ask the Jarl to Use Dragonsreach; Negotiate the Truce (only for `truce_required` outcome) | REGIONAL_ACTION | — | — |

## Season Unending (Conditional)

Story source: [https://en.uesp.net/wiki/Skyrim:Season_Unending](https://en.uesp.net/wiki/Skyrim:Season_Unending)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Ask Arngeir to Host the Peace Council](https://en.uesp.net/wiki/Skyrim:Season_Unending) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Ask the Jarl to Use Dragonsreach; Applicable only when Ask the Jarl to Use Dragonsreach → `truce_required` | REGIONAL_ACTION | — | — |
| [Convince General Tullius to Attend](https://en.uesp.net/wiki/Skyrim:Season_Unending) (REQUIRED) | Castle Dour → Solitude | Ask Arngeir to Host the Peace Council; Applicable only when Ask the Jarl to Use Dragonsreach → `truce_required` | REGIONAL_ACTION | — | — |
| [Convince Ulfric Stormcloak to Attend](https://en.uesp.net/wiki/Skyrim:Season_Unending) (REQUIRED) | Palace of the Kings → Windhelm | Ask Arngeir to Host the Peace Council; Applicable only when Ask the Jarl to Use Dragonsreach → `truce_required` | REGIONAL_ACTION | — | — |
| [Negotiate the Truce](https://en.uesp.net/wiki/Skyrim:Season_Unending) (REQUIRED) | High Hrothgar → High Hrothgar / Throat of the World | Convince General Tullius to Attend; Convince Ulfric Stormcloak to Attend; Applicable only when Ask the Jarl to Use Dragonsreach → `truce_required` | REGIONAL_ACTION | — | — |

## Paarthurnax (Optional)

Story source: [https://en.uesp.net/wiki/Skyrim:Paarthurnax_(quest)](https://en.uesp.net/wiki/Skyrim:Paarthurnax_(quest))

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Kill Paarthurnax](https://en.uesp.net/wiki/Skyrim:Paarthurnax_(quest)) (REQUIRED) | Throat of the World → High Hrothgar / Throat of the World | Drive Alduin from the Throat of the World | REGIONAL_ACTION | — | — |
| [Report Paarthurnax's Death to the Blades](https://en.uesp.net/wiki/Skyrim:Paarthurnax_(quest)) (REQUIRED) | Sky Haven Temple → Markarth | Kill Paarthurnax | REGIONAL_ACTION | — | — |

## The World-Eater's Eyrie (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie](https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Release Odahviing and Depart for Skuldafn](https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie) (REQUIRED) | Dragonsreach → Whiterun | Capture and Interrogate Odahviing | REGIONAL_ACTION | — | One-way access; Departure begins a one-way expedition. Finish preparations before releasing Odahviing. |
| [Acquire the Diamond Claw](https://en.uesp.net/wiki/Skyrim:Diamond_Claw) (REQUIRED) | Skuldafn → Skuldafn | Release Odahviing and Depart for Skuldafn | REGIONAL_ACTION | Artifacts & Collectibles / Dragon Claws / Diamond Claw (REQUIRED) | Missable; One-way access; Expires after Enter Sovngarde; Skuldafn cannot be revisited normally after entering Sovngarde. |
| [Use the Diamond Claw](https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie) (REQUIRED) | Skuldafn → Skuldafn | Acquire the Diamond Claw | REGIONAL_ACTION | — | One-way access |
| [Defeat Nahkriin](https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie) (REQUIRED) | Skuldafn → Skuldafn | Use the Diamond Claw | REGIONAL_ACTION | — | One-way access |
| [Obtain the Nahkriin Mask](https://en.uesp.net/wiki/Skyrim:Nahkriin_(item)) (ASSOCIATED) | Skuldafn → Skuldafn | Defeat Nahkriin | REGIONAL_ACTION | Artifacts & Collectibles / Dragon Priest Masks / Skuldafn Expedition (REQUIRED) | Missable; One-way access; Expires after Enter Sovngarde; Nahkriin cannot be revisited after leaving Skuldafn normally. |
| [Open the Portal to Sovngarde](https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie) (REQUIRED) | Skuldafn → Skuldafn | Defeat Nahkriin | REGIONAL_ACTION | — | One-way access; Do not enter until every remaining Skuldafn objective is complete. |
| [Learn a word of Storm Call at Skuldafn](https://en.uesp.net/wiki/Skyrim:Storm_Call) (ASSOCIATED) | Skuldafn → Skuldafn | Release Odahviing and Depart for Skuldafn | REGIONAL_ACTION | Shouts / Storm Call / Skuldafn (REQUIRED) | Missable; One-way access; Expires after Enter Sovngarde; The Skuldafn word wall cannot be revisited normally after departure. |
| [Enter Sovngarde](https://en.uesp.net/wiki/Skyrim:The_World-Eater%27s_Eyrie) (REQUIRED) | Skuldafn → Skuldafn | Open the Portal to Sovngarde | REGIONAL_ACTION | — | One-way access; Entering permanently ends normal access to Skuldafn. |

## Sovngarde (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Sovngarde_(quest)](https://en.uesp.net/wiki/Skyrim:Sovngarde_(quest))

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Reach the Hall of Valor and Rally the Heroes](https://en.uesp.net/wiki/Skyrim:Sovngarde_(quest)) (REQUIRED) | Sovngarde → Sovngarde | Enter Sovngarde | REGIONAL_ACTION | — | One-way access |

## Dragonslayer (Required)

Story source: [https://en.uesp.net/wiki/Skyrim:Dragonslayer](https://en.uesp.net/wiki/Skyrim:Dragonslayer)

| Task | Location → Region | Prerequisites / applicability | Behavior | Other memberships | Warnings |
|---|---|---|---|---|---|
| [Defeat Alduin in Sovngarde](https://en.uesp.net/wiki/Skyrim:Dragonslayer) (REQUIRED) | Sovngarde → Sovngarde | Reach the Hall of Valor and Rally the Heroes | REGIONAL_ACTION | — | One-way access |
| [Receive Call of Valor and Return to Skyrim](https://en.uesp.net/wiki/Skyrim:Dragonslayer) (REQUIRED) | Sovngarde → Sovngarde | Defeat Alduin in Sovngarde | REGIONAL_ACTION | Shouts / Call of Valor / Sovngarde (REQUIRED) | One-way access |

## Conditional and optional behavior

### Season Unending

`Ask the Jarl to Use Dragonsreach` requires the user to record the observed Skyrim outcome. `TRUCE_REQUIRED` activates the four Season Unending Tasks and makes the truce a prerequisite for capturing Odahviing. `TRUCE_BYPASSED` leaves those Tasks derived Not Applicable and permits capture after the Jarl step. No placeholder Civil War Tasks are invented.

### The Fallen adviser routes

Paarthurnax, Arngeir, and Esbern are three physical alternatives at their actual Locations. Completing any one satisfies the Jarl prerequisite and makes the two unused routes derived Not Applicable. Their prior user state remains stored beneath that derived exclusion.

### Paarthurnax

The Story is Optional and cannot block Skyrim Main Quest collection completion. Task Explorer offers a ledger-only `Resolve as Spared` action; it creates no artificial planner Task. Spared excludes Kill/Report. Completing Kill after that resolution requires confirmation and changes the resolution to Killed. Resetting the resolution restores automatic evaluation.

## One-way destinations

### Skuldafn

The required chain is Departure → acquire Diamond Claw → use Diamond Claw → defeat Nahkriin → open portal → enter Sovngarde. The Nahkriin mask and Storm Call are associated Main Quest objectives but required only in their collectible ledgers. Both expire to derived Not Applicable if incomplete when Enter Sovngarde completes, while their underlying manual state is preserved. Skuldafn remains hidden from operational special destinations until departure is complete; departure guidance derives from the Region metadata.

### Sovngarde

Sovngarde work remains locked and its special destination hidden until `Enter Sovngarde` is complete. Call of Valor is represented once and has both required Main Quest and Shout memberships.

## Completion accounting

Required memberships define a Story denominator; Associated memberships are contextual only. Optional Stories do not contribute to parent-collection completion. Conditional Stories contribute only while active. Derived Not Applicable Tasks are removed from achievable denominators. Overall totals deduplicate by canonical Task ID.

## Known modeling boundary

Golden Claw and Bleak Falls shout objectives retain their own objective prerequisites and do not inherit Farengar gating from an Associated Main Quest membership. Alternate activation details that belong to future Side Quest population are intentionally not fabricated. No unresolved Main Quest modeling concern or geography correction remains for Increment 2B.
