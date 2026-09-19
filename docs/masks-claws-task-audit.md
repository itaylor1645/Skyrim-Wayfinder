# Masks + Claws Task Audit

Generated from the canonical dataset. Do not edit by hand.

- Dragon Priest Mask identities: 14
- Dragon Claw identities: 11
- Collectible definitions: 25
- Collectible credits: 27
- Distinct acquisition Tasks: 27
- Reused acquisition Tasks: 4

| Collection | Collectible | Rule | Required | Acquisition Task(s) | Access / prerequisite |
|---|---|---:|---:|---|---|
| Dragon Claws | Amethyst Claw | ALL | 2 | `claw_amethyst_left_vahloks_tomb`<br>`claw_amethyst_right_vahloks_tomb` | `access_vahloks_tomb`<br>`access_vahloks_tomb` |
| Dragon Claws | Coral Dragon Claw | ANY | 1 | `claw_coral_buy_winterhold`<br>`claw_coral_yngol_barrow` | None |
| Dragon Claws | Diamond Claw | ALL | 1 | `claw_diamond_skuldafn` (reused) | `mq_world_eater_depart_skuldafn` |
| Dragon Claws | Ebony Claw | ALL | 1 | `claw_ebony_korvanjund` | `access_korvanjund` |
| Dragon Claws | Emerald Dragon Claw | ALL | 1 | `claw_emerald_reachwater` | None |
| Dragon Claws | Glass Claw | ALL | 1 | `claw_glass_forelhost` | None |
| Dragon Claws | Golden Claw | ALL | 1 | `collectible_golden_claw_recover` (reused) | None |
| Dragon Claws | Iron Claw | ALL | 1 | `claw_iron_valthume` | None |
| Dragon Claws | Ivory Dragon Claw | ALL | 1 | `claw_ivory_folgunthur` | None |
| Dragon Claws | Ruby Dragon Claw | ALL | 1 | `claw_ruby_dead_mens_respite` | `access_dead_mens_respite` |
| Dragon Claws | Sapphire Dragon Claw | ALL | 1 | `claw_sapphire_ivarstead` | `access_sapphire_claw_reward` |
| Dragon Priest Masks | Ahzidal | ALL | 1 | `mask_ahzidal` | `access_kolbjorn_depths` |
| Dragon Priest Masks | Dukaan | ALL | 1 | `mask_dukaan` | None |
| Dragon Priest Masks | Hevnoraak | ALL | 1 | `mask_hevnoraak` | None |
| Dragon Priest Masks | Konahrik | ALL | 1 | `mask_konahrik` | `prep_konahrik_masks` |
| Dragon Priest Masks | Krosis | ALL | 1 | `mask_krosis` | None |
| Dragon Priest Masks | Miraak | ALL | 1 | `mask_miraak` | `access_waking_dreams` |
| Dragon Priest Masks | Morokei | ALL | 1 | `mask_morokei` (reused) | `college_staff_magnus_accept` |
| Dragon Priest Masks | Nahkriin | ALL | 1 | `mask_nahkriin` (reused) | `mq_skuldafn_defeat_nahkriin` |
| Dragon Priest Masks | Otar | ALL | 1 | `mask_otar` | None |
| Dragon Priest Masks | Rahgot | ALL | 1 | `mask_rahgot` | None |
| Dragon Priest Masks | Vokun | ALL | 1 | `mask_vokun` | None |
| Dragon Priest Masks | Volsung | ALL | 1 | `mask_volsung` | None |
| Dragon Priest Masks | Wooden Mask | ALL | 1 | `mask_wooden` | None |
| Dragon Priest Masks | Zahkriisos | ALL | 1 | `mask_zahkriisos` | `access_bloodskal_barrow` |

## Special behavior

- Coral Dragon Claw: either distinct acquisition Task supplies its single required credit; completing one derives the unused route as Not Applicable.
- Amethyst Claw: the left and right half Tasks each supply one of two required credits.
- Konahrik: `prep_konahrik_masks` confirms current possession after the nine historic prerequisite identities are complete.
- Nahkriin retains its Sovngarde expiration and Skuldafn one-way warning.
- Miraak is missable and gated by `access_waking_dreams`, with a loot-before-leaving warning and no fabricated expiration.
- Kyne's Peace at Shroud Hearth Barrow now requires `claw_sapphire_ivarstead`; the temporary `access_shroud_hearth_depths` bridge was removed.

## Cross-memberships retained

- `claw_diamond_skuldafn`: `claw_diamond` (REQUIRED), `mq_world_eater_eyrie` (REQUIRED)
- `collectible_golden_claw_recover`: `claw_golden` (REQUIRED), `side_golden_claw` (REQUIRED), `mq_bleak_falls` (ASSOCIATED)
- `mask_morokei`: `mask_labyrinthian` (REQUIRED), `college_staff_magnus` (ASSOCIATED)
- `mask_nahkriin`: `mask_skuldafn` (REQUIRED), `mq_world_eater_eyrie` (ASSOCIATED)
