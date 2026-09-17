# Skyrim Wayfinder

Skyrim Wayfinder is a local Windows desktop planner for completion-oriented Skyrim Special Edition playthroughs. It answers: "Given where I am, what useful completion objectives can I do before traveling elsewhere?" Progress is entered manually.

## Increment 1 scope

The functional MVP provides:

- a Regional Planner dynamically grouped by canonical Location, with grouped region choices and access/departure guidance;
- an independently scrolling, collapsible Preparation sidebar;
- a hierarchical multi-membership Task Explorer/completion ledger with a persisted completed-objective filter;
- authoritative `Task -> Location -> TravelRegion` geography;
- prerequisite, minimum-level, branch-exclusion, missable, and one-way rules;
- Done, Deferred, Blocked, Active, manual Not Applicable, and Reset to Automatic actions;
- local SQLite persistence; and
- 38 representative atomic, source-auditable objectives rather than a complete Skyrim database.

Creation Club content, mod content, save parsing, inventory synchronization, maps, routing, cloud sync, and full game coverage are not implemented.

## Geography Foundation

The canonical geography layer currently contains 21 Survival-planning Travel Regions and 235 player-meaningful Locations needed by the approved official Skyrim, Dawnguard, Hearthfire, and Dragonborn completion scope. This phase adds geography only; it does not add future quest Tasks or prerequisite logic.

- `Location.region_id` is the sole authoritative Region assignment.
- Every Location records a broad type, official content origin, factual source URLs, assignment rationale, and verification status.
- Borderline assignments remain fully assigned but are marked `REVIEW_REQUIRED` and listed in the generated [geography catalog review](docs/geography-catalog-review.md).
- [geography-coverage.json](docs/geography-coverage.json) records which planned completion domains require every Location.
- `scripts/generate_geography_review.py` regenerates the human-readable review artifact from canonical data and the coverage inventory.

Bulk Task authoring against unresolved geography is intentionally deferred until Product review.

## Setup (PowerShell)

Python 3.10-3.14 is supported. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

This installs dependencies only in the project-local virtual environment.

## Launch

Double-click `Skyrim Wayfinder.bat` in the repository folder, or launch from PowerShell:

```powershell
.\.venv\Scripts\python -m skyrim_wayfinder
```

User state is written to `%LOCALAPPDATA%\SkyrimWayfinder\wayfinder.sqlite3`, not the repository.

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```

## Architecture

- `domain/` contains completion taxonomy, authoritative geography, planner behaviors, tasks, memberships, and task states.
- `services/` evaluates availability, preserves manual state beneath derived exclusions, generates Location cards, and applies confirmed branch choices.
- `persistence/` stores only user/playthrough state in SQLite.
- `data/canonical/` contains version-controlled JSON definitions and source URL metadata.
- `docs/geography-coverage.json` traces canonical Locations to planned completion domains; the geography review is generated from it.
- `ui/` contains PySide6 views and centralized domain/theme presentation.

Canonical definitions are never mutated when progress changes. SQLite stores the user's state, selected region, player level, branch choices, and UI preferences. Stable string IDs join the two layers. A content fingerprint makes fresh canonical loads reproducible and auditable.

Completion taxonomy and geography are independent. Tasks can have multiple ledger memberships while retaining one state record. Physical Tasks reference one Location, each Location belongs to one Travel Region, and Tasks never override that Region.

## Current limitations

- The dataset is deliberately representative, not comprehensive.
- `The Fallen Completed` is a non-recommended bookkeeping milestone because intermediate main quests are not in this increment; it prevents Skuldafn from unlocking from an inaccurate shortened quest chain.
- Meridia's Beacon is currently opportunistic and remains out of normal recommendations because its destination is randomized.
- Gold and inventory quantities are not tracked. The player confirms preparation manually.
- Executable packaging is deferred; the included batch file launches the project-local development environment.
