# Skyrim Wayfinder

Skyrim Wayfinder is a local Windows desktop planner for completion-oriented Skyrim Special Edition playthroughs. It answers: “Given where I am, what useful objectives can I do before traveling elsewhere?” Progress is entered manually; the app does not read Skyrim saves.

## Current scope

The Regional Planner groups actionable objectives by physical Location so one card shows the work available during that visit. The completion ledger groups the same canonical Tasks by domain, collection, and Story; a Task can appear in multiple branches without duplicating its state. Preparation has a collapsible sidebar, and completed ledger objectives can be hidden.

Canonical content currently includes the Skyrim Main Quest, official Shouts, Dragon Priest Masks, Dragon Claws, Daedric Artifacts, the Companions, the College of Winterhold, and the Thieves Guild. Nine College-derived Unique Spells & Powers are included. These are authored increments, **not complete coverage of every Skyrim quest or collectible**. The dataset currently has 417 Tasks and 167 Stories.

The Thieves Guild distinguishes finishing the Mercer/Nightingale narrative from fully restoring the Guild and becoming Guild Master. Four manually maintained, finite city-influence counters (Whiterun, Markarth, Solitude, and Windhelm; five qualifying completed jobs each) unlock the corresponding special jobs. Random radiant jobs and their destinations are not permanent completion objectives.

## Geography foundation

The catalog contains 21 Survival-planning Travel Regions and 248 verified, player-meaningful Locations, with no `REVIEW_REQUIRED` assignments. These regions represent practical staging hubs, not necessarily official Hold boundaries.

- Each physical Task references one Location; each Location belongs to exactly one Travel Region. A Task cannot override its Region.
- Locations record type, official content origin, source URLs, assignment rationale, and access metadata.
- [Geography coverage](docs/geography-coverage.json) traces Locations to planned domains. The generated [geography catalog review](docs/geography-catalog-review.md) shows current assignments.
- `scripts/generate_geography_review.py` regenerates the review from canonical data and the coverage inventory.

## Setup and launch (PowerShell)

Python 3.10–3.14 is supported. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Double-click `Skyrim Wayfinder.bat`, or launch from PowerShell:

```powershell
.\.venv\Scripts\python -m skyrim_wayfinder
```

Dependencies stay in the project-local virtual environment. User progress is stored in `%LOCALAPPDATA%\SkyrimWayfinder\wayfinder.sqlite3`, outside the repository. An `.exe` or installer is not supplied yet.

## Tests and audits

```powershell
.\.venv\Scripts\python -m pytest
```

Generated content reviews include the [Main Quest](docs/main-quest-task-audit.md), [Shouts](docs/shout-task-audit.md), [Masks and Claws](docs/masks-claws-task-audit.md), [Daedric Artifacts](docs/daedric-artifacts-task-audit.md), [Companions](docs/companions-task-audit.md), [College](docs/college-task-audit.md), and [Thieves Guild](docs/thieves-guild-task-audit.md) audits. Each records scope, prerequisites, geography, cross-memberships, and source links relevant to its increment.

## Architecture and state

- `src/skyrim_wayfinder/domain/` defines completion taxonomy, authoritative geography, planner behaviors, Tasks, memberships, access conditions, and finite-progress definitions.
- `src/skyrim_wayfinder/services/` evaluates availability, groups regional Location cards, and derives progress from canonical prerequisites while retaining manual corrections.
- `src/skyrim_wayfinder/persistence/` stores only user/playthrough state in SQLite: Task status, observed outcomes, choices, access overrides, Guild influence counts, selected region, player level, and UI preferences.
- `src/skyrim_wayfinder/data/canonical/` contains version-controlled JSON definitions and source metadata; `src/skyrim_wayfinder/ui/` contains the PySide6 interface.

`AVAILABLE` and `LOCKED` are derived. Users can mark Tasks Done, Deferred, Blocked, Active, or Not Applicable, and reset them to automatic evaluation. A temporary derived branch exclusion does not overwrite an unrelated stored manual state. Completing a historical acquisition remains recorded even if its prerequisite is later corrected or the item is subsequently surrendered; the Skeleton Key is an example.

## Boundaries

Creation Club and mod content, save parsing, inventory synchronization, maps, routing, and cloud sync are out of scope. The current Thieves Guild increment intentionally excludes repeatable job identities, Stones of Barenziah, the Dragonborn quest *Paid in Full*, broad unique-equipment collection, and a mutable Nightingale-power collection. Other factions and side-quest catalogs remain future work.
