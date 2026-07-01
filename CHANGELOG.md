# Changelog

- All notable changes to ATOMVS Time Planner will be documented in this file.
- The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Archive lifecycle for Habit — `delete_habit` now soft-deletes via an `archived_at` timestamp; a dedicated `purge_habit` performs the administrative hard delete (CLI `habit purge <id>` with literal "purge" confirmation, listing the TimeLogs/instances it will destroy); `restore_habit` reverses an archive; `habit list --archived` lists archived habits. Schema migration `migration_004_habit_archive` (idempotent `ALTER TABLE ADD COLUMN` via `PRAGMA table_info`). Standard listings and `HabitInstanceService.generate_instances` exclude archived habits. Preserves HabitInstance and TimeLog history, the core of the product. Implements BR-HABIT-005 (rewritten) and BR-HABIT-006 (new). (Closes #61)
- `habit skip` justification flags — `--reason` (justified skip, optionally with `--note`) and `--unjustified` (deliberate skip without justification), mutually exclusive; the distinction feeds adherence metrics that previously could not tell an intentional skip from a missing record. (ADR-058)
- C4 model in Structurizr DSL (`docs/architecture/workspace.dsl`) — versionable canonical source for the architecture views.
- ADR-056: Selective adoption of Object Calisthenics
- ADR-057: Archive Lifecycle for Habit (Accepted; implementation errata 2026-06-05)
- ADR-058: `habit skip` reason/unjustified CLI flags
- ADR-059: Snapshot clock determinism
- DT-075: Phantom BR-EVENT-002 vs BR-REORDER-XXX nomenclature drift (planned for v1.7.5)
- DT-076: TimerScreen placeholder with 5 TODOs to TimerService (planned for v1.8.0)
- DT-077: Historical drift `__version__` 0.1.0 vs pyproject.toml — resolved retroactively in v1.7.3

### Changed

- `HabitService.delete_habit` semantics — archives (`archived_at = datetime.now()`, naive local, per BR-TASK-009 convention) instead of hard-deleting; `get_habit` does not filter archived habits (administrative inspection). (BR-HABIT-005)
- `roadmap.md` bumped to v10.0.0 absorbing v1.7.2 and v1.7.3, current metrics (1.402 tests, 120 BRs, 52 active ADRs)
- `sprints.md` v8.0.0 marked as `[HISTORICAL]` — operational tracking migrated to GitLab Issues as Single Source of Truth
- `technical-debt.md` bumped to v2.34.0 (DT-074 resolved, DT-075/076/077 added, alignment with current roadmap)
- Architectural assessments moved from versioned tree to `docs/wiki/` (gitignored) — assessment artifacts are temporal diagnostics by nature; actionable findings live as DTs/ADRs/issues

### Fixed

- E2E snapshot determinism — an autouse fixture restricted to the snapshot modules freezes the clock with `freeze_time(..., tick=True)`; snapshots are back in the pre-push and CI gates (`--ignore` removed). `tick=True` keeps `time.monotonic()` advancing so asyncio still schedules modal transitions under the freeze, while date and minute stay fixed. (ADR-059, closes #66)
- Flaky TUI keybinding tests (BR-TUI-021) — the single post-event `pilot.pause()` is replaced by a `_wait_until` polling helper that pumps the message loop until the predicate holds or a cycle cap is reached, deterministic on both fast and CI-contended runners. (Closes #67)
- DT-074: BRs and Humble Objects without test coverage — closed in v1.7.2; documented as resolved
- Gitflow technical debt: `main` had been frozen at v1.7.2 since mid-April while `develop` accumulated v1.7.3 + Sessão 29 housekeeping. Synchronization performed without release-cut as a transitional sync; next tag will be v1.8.0 when archive lifecycle ships. (Refs #64)

### Notes

- Archive lifecycle (BR-HABIT-006) is implemented and merged to `develop`; the next release tag will be **v1.8.0**. Implementation plan retained at `docs/wiki/Session-29-Implementation-Plan-Habit-Archive.md` (gitignored).
- v1.8.0 will additionally include namespace rename `src/timeblock/` → `src/atomvs/` (ADR-045/050) and Agenda/Sidebar redesign (ADR-041/042)

---

## [1.7.3] - 2026-05-01

### Fixed

- **logger:** Removed silent auto-configuration in `get_logger()` that added `StreamHandler(stderr)` before `main()` could call `configure_logging(console=False)`, fixing log leakage that overlapped with the Textual layout in the TUI. Fix aligned with BR-OBS-001 rules 11-12. (Closes #48)
- **habit-instance:** `HabitInstanceService.generate_instances` is now idempotent — repeated calls for the same period no longer create duplicate HabitInstance rows, per BR-HABIT-003 ("Não duplica instâncias existentes"). (Closes #2)
- **version:** Unified `__version__` reading via `importlib.metadata`, eliminating the historical drift between `pyproject.toml` (correct) and `src/timeblock/__init__.py` (frozen at the 0.1.0 placeholder). Single source of truth is now `pyproject.toml`.

---

## [1.7.2] - 2026-04-13

### Added

- BR-TIMER-010: Activity tracking during timer pause
- BR-DATA-002: Backup strategy formalization
- ADR-048: Feature toggles for incremental release
- ADR-049: Two-phase activity tracking during pauses
- ADR-051: Three-phase backup strategy (CLI/auto/remote)
- Script: scripts/migrate_backups_to_xdg.py to relocate legacy backups from src/data/backups to ~/.local/share/atomvs/backups

### Changed

- HeaderBar: Now uses native border_title (active routine name) and border_subtitle (full date) instead of manually composed title
- HeaderBar: Date format updated to "Weekday, DD de Month de YYYY" with proper Portuguese preposition
- HeaderBar: Placeholder "Sem rotina ativa" shown when no routine is configured
- HeaderBar: Screen label removed from top bar (already present in sidebar)
- HeaderBar: TASKS label translated to TAREFAS for Portuguese consistency
- Agenda: Blocks redesigned with icon prefix and dotted body marker replacing left accent bar
- Agenda: Vertical ruler between hour column and blocks removed for cleaner layout
- Agenda: Spacing between hour label and block content tightened
- Status bar: Keybinding hints now use parentheses instead of brackets for better terminal rendering
- Status bar: Dotted separator (·) added between consecutive hints for improved readability
- TimerPanel: Elapsed time now displays HH:MM:SS when exceeding 60 minutes (Closes #5)
- Dashboard: Panel order reorganized to prioritize timer, habits, tasks, metrics (refs #31)

### Fixed

- Backup service: backup_dir now resolves via XDG spec ($XDG_DATA_HOME/atomvs/backups) instead of deriving from db_path.parent, preventing user data from being written inside the code repository (Closes #47)
- Color documentation: BR-TUI color mapping reconciled with implementation (pending status is C_INFO blue, not Overlay0 gray as previously documented)

---

## [1.7.1] - 2026-04-08

### Added

- Logging: sys.excepthook global for uncaught exceptions (CRITICAL level)
- Logging: TUI \_handle_exception override logs before Textual crash handler
- Logging: All CLI commands now log errors to JSON Lines file
- Logging: 21 bare-pass except blocks in TUI widgets/screens replaced with logger.debug
- Architecture diagram: docs/diagrams/architecture/system-overview.md (Mermaid)

### Changed

- README: Updated to ATOMVS Time Planner branding, badges (1345 tests, 82% coverage), stack, docs structure (Diataxis), roadmap
- README: ASCII diagrams corrected (TAG added, OVERDUE removed, CANCELLED in timer, keybindings)
- README: Mermaid diagram links below each ASCII diagram
- Diagrams: 14 diagrams audited — 2 removed, 5 updated, 9 rewritten to match v1.7.0 codebase
- technical-debt.md: 5 DTs reclassified as features (DT-019, DT-060, DT-063, DT-065, DT-069) moved to roadmap v1.8.0
- roadmap.md: New v1.8.0 section with 7 planned features

### Fixed

- main.py: launch_tui() no longer silences migration exceptions (was except:pass)
- main.py: Migration success now logged with count

---

## [1.7.0] - 2026-04-05

### Added

- TUI: Complete interactive dashboard with 5 functional panels (Habits, Tasks, Timer, Metrics, Agenda)
  - Textual framework with Tab/Shift+Tab navigation and internal cursor (j/k)
  - FocusablePanel as base for interactive panels with keyboard navigation
  - Color system with semantic tokens and WCAG-compliant palette (Catppuccin Mocha)
  - TCSS modularized into 7 files (base, layout, cards, dashboard, statusbar, timer, forms)
- TUI: Dashboard-first CRUD with contextual modals (ADR-034)
  - Create, edit and delete routines, habits and tasks via keybindings (n/e/x)
  - Reusable FormModal and ConfirmDialog widgets
  - PlaceholderActivated message for creation from empty state (BR-TUI-013)
- TUI: Quick actions on HabitsPanel — done (v), skip (s), timer (t), undo (u)
- TUI: Live timer with per-second updates, pause/resume/stop/cancel
- TUI: MetricsPanel with streak, completeness and weekly heatmap (BR-TUI-033, ADR-047)
  - Persistent best_streak via migration_003 (best_streak column on routines)
  - Retroactive PENDING instance generation for days without records (R8)
  - Keybinding f cycles display period between 7d/14d/30d (R7/R13)
  - Completeness calculated for 7d, 14d and 30d windows
  - Heatmap shows done/total per day with check marks
- TUI: Contextual footer with dynamic keybindings per focused panel (BR-TUI-007)
- TUI: Agenda with auto-refresh every 60s and auto-scroll to current time (BR-TUI-003-R15)
- TUI: StatusBar with active routine, contextual keybindings and timer elapsed
- TUI: Empty state with placeholder guidance in all panels
- TUI: Screen navigation — Dashboard, Routines, Habits, Tasks, Timer
- TUI: Widget system — NavBar, CommandBar, HelpOverlay, StatusBar, TimeblockGrid
- CLI: `atomvs demo create` with 3 mock routines and 8 tasks (BR-TUI-003-R28)
- CLI: `atomvs demo clear` to remove demo data (respects FK constraints)
- BDD: 8 TUI feature files in Gherkin format (61 scenarios)
- migration_003: best_streak column on routines table
- ADR-031 through ADR-047: 17 new architectural decisions documented
- docs: BR-TUI-001 through BR-TUI-033 (33 TUI business rules)
- docs: Refactoring plan RF-001 through RF-010 based on Fowler (2018) and Humble & Farley (2010)

### Changed

- CLI: Entry point changed from `timeblock.main:app` to `timeblock.main:main` (TUI opens with `atomvs` without args)
- CI/CD: Pipeline optimized from 10 to 8 jobs
- CI/CD: GitHub Actions aligned with GitLab CI consolidation
- CI/CD: Test timeout increased to 45min for test:all, 60min for integration
- Navigation keybinding changed from j/i to j/k (vim industry standard)
- Contextual footer displays placeholder hints when empty panel is focused (DT-066)
- Snapshot testing guide rewritten with real data (17 tests / 19 baselines)
- BR-TUI-033-R5: Streak semantics corrected — no grace period, streak breaks on first non-100% day

### Fixed

- DT-059: Migration messages on stdout replaced with logger
- DT-064: CVEs resolved (aiohttp 3.13.5, Pygments 2.20.0)
- DT-066: Placeholder hints moved from panel body to contextual footer
- DT-068: Habits not sorted by scheduled_start

### Metrics

- Total tests: ~1,340 (1,336 passed, +558 since v1.6.0)
- Distribution: Unit ~1,050 (78%), Integration ~130 (10%), BDD ~61 (5%), E2E ~95 (7%)
- Global coverage: ~82% (threshold 80%)
- BRs formalized: 115+ (+34 TUI since v1.6.0)
- ADRs: 47 documented (+15 since v1.6.0)
- DTs: 51 resolved / 66 total (77%)
- Pipeline: 8 jobs (~10min CI)

---

## [1.6.0] - 2026-02-12

### Added

- CI/CD: Docker image with pre-installed dependencies (Dockerfile.ci)
- CI/CD: DevSecOps with Bandit (SAST) and pip-audit (SCA)
- CI/CD: Combined coverage from 4 suites via coverage run
- CI/CD: Updated pre-commit hooks (ruff on commit, full suite on push)

### Changed

- refactor: Flattened structure from cli/ to project root
- CI/CD: Pipeline migrated to Docker (eliminates pip install overhead)
- CI/CD: Removed build:docs from pipeline (manual validation)
- CI/CD: GitHub Actions aligned with GitLab CI

### Fixed

- fix: CVE-2026-1703 in pip 25.3 (updated to pip>=26.0)
- fix: pytest-cov auto-combined partials (migrated to coverage run)
- fix: Partial threshold blocked individual jobs (--cov-fail-under=0)

### Metrics

- Total tests: 778 (576 unit, 116 integration, 56 bdd, 30 e2e)
- Global coverage: 87% (threshold 85%)
- Pipeline: 9 jobs (quality + test + coverage + security + sync)
- ADRs: 32 documented

---

## [1.5.0] - 2026-02-03

### Added

- CI/CD: Automatic sync GitLab => GitHub via sync:github job
- CI/CD: GitHub Merge Queue support (merge_group event)
- CI/CD: Sync stage in GitLab pipeline
- docs: cicd-flow.md v2.0 with complete dual-repo architecture

### Changed

- CI/CD: GitLab defined as source of truth
- CI/CD: GitHub configured as public showcase
- CI/CD: Branch protection adjusted for automatic sync

### Fixed

- CI/CD: Divergent histories between GitLab and GitHub
- CI/CD: Token scope workflow for GitHub Actions updates

### Metrics

- Total tests: 873 (+188 since v1.4.1)
- Global coverage: 76% (+5pp since v1.4.1)
- Distribution: Unit 696 (79.7%), Integration 83 (9.5%), BDD 52 (6.0%), E2E 42 (4.8%)
- GitLab CI: 8 jobs (6 test + 1 build + 1 sync)
- Pipeline time: ~3min (local => GitHub sync)

---

## [1.4.1] - 2026-01-30

### Added

- test(e2e): 16 E2E tests for task lifecycle (BR-TASK-001 to 005)
- test(e2e): 12 E2E tests for list command filters
- docs: ATOMVS logo and expanded table of contents in README
- docs: Updated quality-metrics.md with v2.0.0 metrics
- docs: Updated references (SWEBOK v4.0, ISO/IEC/IEEE 29148:2018)

### Metrics

- Total tests: 685 (+172 since v1.4.0)
- Global coverage: 71% (+27pp since v1.4.0)
- E2E tests: 42 (+28)
- Distribution: Unit 513 (75%), Integration 83 (12%), E2E 42 (6%), BDD 7 (1%)

---

## [1.4.0] - 2026-01-28

### Added

- ADR-027: Documentation Tooling (MkDocs + mkdocstrings)
- BR-CLI-002: Multi-format datetime parser (ISO 8601, DD-MM-YYYY, DD/MM/YYYY)
- Section 5 in architecture.md with actual models (Event, PauseLog, ChangeLog)
- Enum documentation: TimerStatus, EventStatus, ChangeType
- Section 7 in architecture.md with 27 categorized ADRs
- glab CLI for GitLab pipeline monitoring

### Fixed

- GitLab/GitHub CI: added `pip install -e .` to resolve ModuleNotFoundError
- mkdocs.yml aligned with consolidated docs/ structure
- Broken links in ADRs and diagrams (DT-009)

### Updated

- Dependencies: sqlmodel 0.0.31, typer 0.21.1, SQLAlchemy 2.0.46, ruff 0.14.14
- pytest 9.0.2, mypy 1.19.1, rich 14.3.1, coverage 7.13.2

### Metrics

- Tests: 513 passing
- Coverage: 44% (unit)
- ADRs: 27 documented
- BRs: 67 formalized
- Mypy: 0 errors

---

## [1.3.2] - 2026-01-22

### Added

- BR-VAL-001: Time Validation (20 unit tests)
- BR-VAL-002: Date Validation (35 unit tests)
- BDD structure for date validation feature
- pyright configuration in pyproject.toml

### Fixed

- Enabled BDD steps for date_validation (BR-VAL-002)
- validate_date import in step definitions

### Metrics

- Tests: 466 → 558 (+92)
- Coverage: 42% (+26pp from v1.3.1)
- Mypy: 0 errors

---

## [1.3.1] - 2026-01-19

### Added

- **ADR-026: Test Database Isolation Strategy**
  - Hybrid strategy: DI for unit, env var for integration
  - Standardized fixtures in conftest.py
  - Documentation in architecture.md section 4.4

- **BR → Tests Coverage Analysis**
  - Complete matrix in quality-metrics.md section 6.1
  - 52 BRs documented, 35 with tests (67%)
  - 17 BRs identified without coverage
  - Updated roadmap with implementation plan

### Changed

- **SSOT for database path**
  - Centralized in `engine.get_db_path()`
  - Removed `DATABASE_PATH` from config.py
  - Eliminated `sys.modules` hacks in tests

- **Simplified integration fixtures**
  - `isolated_db` uses only env var (ADR-026)
  - Removed duplicate local fixtures
  - `test_init.py` uses specific `empty_db_path`

### Fixed

- **BR-SKIP-003:** IGNORED can receive retroactive justification (recovery)

### Metrics

- 466 tests passing
- 65% global coverage
- 0 mypy errors
- 26 skipped tests (documented analysis)

---

## [1.3.0] - 2025-11-08

### Added

#### Testing and Quality Consolidation

**Testing Structure:**

- Consolidated structure in `05-testing/` (removed duplicate `07-testing/`)
- Added navigable documents:
  - `testing-philosophy.md` - Project testing philosophy
  - `requirements-traceability-matrix.md` - Complete RTM with BR => Test => Code traceability
  - `test-strategy.md` - Consolidated test strategy
- 5 test scenarios now accessible:
  - event-creation
  - conflict-detection
  - event-reordering
  - habit-generation
  - timer-lifecycle

**Complete Glossary:**

- Glossary expanded to 298 lines in `01-architecture/12-glossary.md`
- All main terms defined (TimeBlock, Habit, HabitInstance, Event, etc)
- HabitAtom marked as DEPRECATED (marketing only)
- Relationships between concepts documented

**Formalized Business Rules:**

- `event-reordering.md` - Complete formal specification (222 lines)
- Fundamental principles: Explicit User Control, Information Without Imposition
- BR-EVENT-001 to BR-EVENT-007 documented
- Purpose change: System only DETECTS conflicts, doesn't propose automatic reordering

**Impact:**

- Consolidated testing structure without duplications
- Complete and precise glossary
- Formally specified Business Rules
- Philosophy alignment: user always in control

---

## [1.2.2-logging] - 2025-11-10

### Added

#### Structured Logging System - Sprint 1.3

**Logging Module:**

- `cli/src/timeblock/utils/logger.py` (118 lines)
  - `setup_logger()` with rotating file handler
  - `get_logger()` helper to obtain configured logger
  - `disable_logging()` / `enable_logging()` for tests
  - Structured format: `[timestamp] [level] [module] message`
  - Console and file support with automatic rotation (10MB, 5 backups)

**Tests:**

- test_habit_lifecycle.py: E2E test
- test_logging_integration.py: Integration
- test_logger.py: Unit tests
- test_habit_instance_service_extended.py
- Test coverage: 43% -> 83%

**Documentation:**

- PHILOSOPHY.md, ARCHITECTURE.md
- ADRs 015-018 (HabitAtom refactor)
- logging-strategy.md
- HabitAtom Sprints docs

---

## [1.2.1-docs] - 2025-11-11

### Added

#### Documentation Reorganization and Consolidation

**Documentation Structure:**

- 9 ADRs now navigable in mkdocs (ADR-012 to ADR-020)
  - ADR-012: Sync Strategy
  - ADR-013: Offline-First Schema
  - ADR-014: Sync UX Flow
  - ADR-015: HabitInstance Naming
  - ADR-016: Alembic Timing
  - ADR-017: Environment Strategy
  - ADR-018: Language Standards
  - ADR-019: Test Naming Convention
  - ADR-020: Business Rules Nomenclature

**Architecture Consolidation:**

- Unified structure in `01-architecture/` (removed `02-architecture/` and `01-guides/`)
- Added navigable documents:
  - `00-architecture-overview.md` - Consolidated overview (20KB)
  - `16-sync-architecture-v2.md` - Sync architecture v2.0
  - `17-user-control-philosophy.md` - User control philosophy (15KB)
  - `18-project-philosophy.md` - Atomic habits philosophy (12KB)

**Impact:**

- 20 navigable ADRs (vs 11 previously) = +82%
- Organized docs/ structure without duplications
- Project philosophy and principles documented

---

## [1.1.0] - 2025-11-01

### Added

#### Event Reordering System - Complete Implementation

- Automatic conflict detection between scheduled events
- Priority calculation based on status and deadlines (CRITICAL, HIGH, NORMAL, LOW)
- Sequential reordering algorithm respecting priorities
- Interactive confirmation before applying changes
- New CLI command: `timeblock reschedule [preview] [--auto-approve]`

**Enhanced Services:**

- `TaskService.update_task()` now returns tuple with optional ReorderingProposal
- `HabitInstanceService.adjust_instance_time()` integrated with conflict detection
- `TimerService.start_timer()` detects conflicts when starting timers

**New Components:**

- `EventReorderingService` - Central reordering logic (90% test coverage)
- `event_reordering_models.py` - Data structures (EventPriority, Conflict, ProposedChange, ReorderingProposal)
- `proposal_display.py` - Rich formatted CLI output for proposals
- `reschedule.py` - CLI command implementation

**Tests:**

- 78 new tests (219 total, +55% increase)
- 100% coverage in event_reordering_models
- 90% coverage in event_reordering_service
- Integration tests for all affected services

**Documentation:**

- Complete technical documentation in `docs/10-meta/event-reordering-completed.md`
- Sprint retrospective in `docs/10-meta/sprints-v2.md`
- Architecture and API documentation updated

### Changed

- Services now return tuples where appropriate to include reordering proposals
- Enhanced error messages with conflict information

### Breaking Changes

- None

### Performance

- Conflict detection optimized for O(n log n) complexity
- Efficient event queries in date ranges

---

## [1.0.0] - 2025-10-16

### Added

- Initial baseline release
- SQLite database initialization
- Basic CRUD operations for events
- Event listing with filters (day, week)
- Brazilian time format support (7h, 14h30)
- Basic conflict detection (warning only, non-blocking)
- Support for events crossing midnight
- 141 tests with 99% coverage

**CLI Commands:**

- `timeblock init` - Initialize database
- `timeblock add` - Create events
- `timeblock list` - List events with filters

### Known Limitations

- No recurring habits
- No automatic reordering
- No reports or analytics
- Basic CLI (no TUI)

---

[Unreleased]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.7.3...HEAD
[1.7.3]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.7.2...v1.7.3
[1.7.2]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.7.1...v1.7.2
[1.7.1]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.2.2-logging...v1.3.0
[1.2.2-logging]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.2.1-docs...v1.2.2-logging
[1.2.1-docs]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.1.0...v1.2.1-docs
[1.1.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/releases/tag/v1.0.0
