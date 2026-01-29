# Task Summary: manual-metadata-and-versioning

## 1. Project Snapshot
System state after Build System implementation and Manual restructuring.

- **Architecture Overview**:
    - **Core**: Python TUI (`prompt_toolkit`).
    - **Build**: `setup.py` (Dev Tool) -> PyInstaller (Exe) -> Inno Setup (Installer).
    - **Data**: `schemas/` (Markdown with YAML headers).
    - **Docs**: `docs/manual/` (Markdown).
- **Key Systems**:
    - `src/ui/screens/settings.py`: Hosts current Doc Viewer (needs upgrade to Vim-like).
    - `src/core/config.py`: Manages paths (needs connection to new `config.json` versioning).
- **Known State**:
    - `legacy/` folder removed.
    - `get_specs_dir` renamed to `get_schemas_dir` globally.
    - Build system verified via simulation and PyInstaller installation.

---

## 2. File-Level Impact Map
Changes made during this session.

* `setup.py`: **[New]**
  * Created TUI build tool (Multi-select).
* `story_lord.spec`: **[New]**
  * PyInstaller configuration.
* `installer.iss`: **[New]**
  * Inno Setup script.
* `docs/manual/`: **[New Directory]**
  * Created structure and basic files (`inputs.md`, `options/`).
* `src/ui/screens/settings.py`: **[New]**
  * Implemented Docs Tree and Viewer.
* `src/core/config.py`: **[Refactor]**
  * `SPECS_DIR` -> `SCHEMAS_DIR`.
* `src/cli.py` & `src/core/*.py`: **[Refactor]**
  * Updated imports to match schema renaming.
* `legacy/`: **[Deleted]**
  * Migrated content to `schemas/`.

---

## 3. Execution Log (Factual Record)
Actions taken in the current session.

- **Objective**: Implement Build System and Restructure Manual.
- **Refactor**: Renamed `specs` folder to `schemas`. updated `src` references.
- **Build**: Installed `pyinstaller`. Created and verified `setup.py` (Dev TUI).
- **Docs**: Created `docs/manual` structure. Updated `README.md`.
- **UI**: Added `Settings` screen with basic documentation viewer.
- **Fixes**: Resolved regression in `src/cli.py` where `get_specs_dir` caused ImportError.
- **Migration**: Moved `legacy` files to `schemas` folders using Python script.

---

## 4. User Intent Record (Source of Truth)

### Raw Instructions
> make it so this has a metadata json at the root manual.json that includes the title and description of each item that is included so it can display the title and short description of the file then display below it Enter to View file at whitch point it will open a fullscreen vie vim like interface to view and scroll through the file also the .md should have a color system to color code the manual instructuins also make it much more detaile and map things like the cli (the --help flag message and more information about it) and the the TUI overall structure ad giving everything its own folder
>
> make the version in the Story lord Title be linked to the C:\Users\santi\Documents\StoryLord\config\config.json file there it will store the current version of the current runtime and and it will map directly to the
>
> git_history
> and make C:\Users\santi\.gemini\antigravity\global_workflows\commit.md support this new versioning system automatically
>
> also the rules for the commit versioning is if its a feature addition its a 0.1 increase if its a bug fix build fix etc it it a 0.0.1 increase if its a large bundle of fetures that constitude a dratic update like a change or architecture but not like a big refactor that will not be public and it hasto constitute a significant upgradeit menaing it makes it better by changing user facing features anything backend and private should not be an upgrade make it so it details that in a file in the manual for development guidelines here also are going to be modding and test dev guides codebase philosphy and architecture overview etc...

---

## 5. Known Failure Patterns
- **Import Renaming**: Renaming core functions (e.g., `get_specs_dir`) requires exhaustive search (`grep`) across `src/` and `tests/`. Missed occurrences caused runtime crashes.
- **Shell Commands**: Windows PowerShell `cp` and `mkdir` with multiple args proved unreliable. Use Python one-liners or scripts for file operations.
- **Setup.py**: Initial `radiolist` prevented multi-task selection. Switched to `checkboxlist`.

---

## 6. Separation of Truth Layers

### Facts
- `legacy` folder is gone.
- `specs` is now `schemas`.
- Apps runs via `src/main.py`.

### Observations
- User wants a "Vim-like" experience for the manual, implying generic `arrow` keys might be insufficient or they specifically want `j/k` bindings and a cleaner, full-screen view.
- Versioning logic is strictly defined (Feature=0.1, Bug=0.0.1) and needs to be automated in the workflow.

### Hypotheses
- The `config.json` path `C:\Users\santi\Documents\StoryLord\config\config.json` might not exist yet and needs verification.
- The `global_workflows\commit.md` modification implies modifying the *AI's* tool-use behavior or the script it runs.

---

## 7. Stability Map
- **Safe**: `docs/manual` (New territory), `setup.py` (Isolated tool).
- **Critical**: `src/core/config.py` (Touching version logic here affects app startup).
- **External**: `global_workflows/commit.md` (Outside repo, proceed with caution).

---

## 8. Antigravity Planning Scaffold

### Phase 1 — Investigation Checklist
- [ ] Check existence of `C:\Users\santi\Documents\StoryLord\config\config.json`.
- [ ] Read content of `C:\Users\santi\.gemini\antigravity\global_workflows\commit.md`.
- [ ] Audit current `settings.py` viewer implementation for reuse vs replacement.

### Phase 2 — Modeling & Diagnosis Guidance
- **Manual Metadata**: simple `manual.json` at `docs/manual/`. Needs a loader in `src/ui/screens/settings.py`.
- **Vim Viewer**: Need a new `FullScreen` or persistent `Window` mode in TUI logic. `prompt_toolkit` keybindings for `j`, `k`, `gg`, `G`, `/` (search).
- **Versioning**: Python script to read/write `config.json` and calculate increment based on commit message prefix (`feat`, `fix`).

### Phase 3 — Implementation Strategy
1.  **Versioning Core**: Implement the version manager first to ensure the "Story Lord Title" can link to it. Validating this early prevents circular dependency with docs.
2.  **Workflow Update**: Modify the commit workflow to use the new version manager.
3.  **Manual System**: Build the `manual.json` generator/reader and the TUI Viewer last.

---
