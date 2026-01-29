# Task Summary: install-system-overhaul

## 1. Project Snapshot
**Story Lord** is a Python-based TUI application for story management.
- **Architecture**: Prompt Toolkit (TUI), PyInstaller (Build), Inno Setup (Installer).
- **Current State**: Stable after fixing a startup crash (`Application` init) and merging to GitHub.
- **Pending/Incomplete**: Configuration file relocation was planned but not executed.
- **New Requirements**: Significant expansion of `setup.py` capabilities and internal file structure reorganization.

---

## 2. File-Level Impact Map
* `src/ui/app.py`: **[fix]**
    * Change: Removed invalid `title` argument from `Application()` causing crash. Removed F1-F4 keybindings.
* `src/core/config.py`: **[Planned Refactor]**
    * Change: Logic to point to `~/.storylord` instead of `~/Documents/StoryLord` is planned but NOT implemented.
* `README.md` & `docs/manual/inputs.md`: **[Minor Tweak]**
    * Change: Removed references to F1-F4 keys.
* `setup.py`: **[Target for Heavy Refactor]**
    * Change: Will need massive expansion for new Install/Uninstall/Repair logic.

---

## 3. Execution Log (Factual Record)
- **Merged to Origin**: Pushed local `main` to `https://github.com/KffeePt/storylord`. Remote was empty, so no unrelated history merge was actually needed.
- **Fixed Crash**: Diagnosed `TypeError: Application.__init__() got an unexpected keyword argument 'title'`. Fixed by removing the argument.
- **Deprecated F-Keys**: Removed F1-F4 bindings from code and docs to rely on the menu system.
- **Planned Config Relocation**: Created an implementation plan to move config to `~/.storylord/config/config.json` to avoid auto-discovery issues in Documents. **This was NOT executed.**

---

## 4. User Intent Record (Source of Truth)

### Raw Instructions (Sanitized)
> **Config Relocation**: "Make it so instead the config lives in ~/.storylord/config/config.json so it doesnt happen [auto discovery]."
>
> **Main Menu**: "Add an option to the main menu to open the config and edit the TUI themes and the config and visualize (readonly the version of the TUI) and also it should be able to update the TUI release file version."
>
> **File Structure**: "Make a Directory in Program files and there it should store the release Installer and the Runtime binaries."
>
> **Setup.py Overhaul**: "Make setup.py even more useful so it can:
> 1. Install (run the setup installer)
> 2. Update/Repair (automatically... if it detects incomplete install with hash verification)
> 3. Uninstall (5 sub options: Keep stories only, Keep config+stories, Remove config only, Remove Stories only, Remove everything)"
>
> **Refactoring**:
> - Move `schemas/_schemas.json` to `schemas.json`.
> - Centralize registry for story nodes in `registry.json`.

---

## 5. Stability Map
- **UI Core (`src/ui/app.py`)**: **Stable**. Recently fixed.
- **Config Core (`src/core/config.py`)**: **Volatile**. Needed changes are defined but not applied.
- **Build System (`setup.py`)**: **Volatile**. Currently simple wrapper, needs to become a complex CLI tool.

---

## 6. Antigravity Planning Scaffold

### Phase 1 — Investigation Checklist
- [ ] **Config Relocation**: Review `src/core/config.py` and `src/core/version_manager.py`. The plan exists in `implementation_plan.md` (previous session) but needs execution.
- [ ] **Setup Logic**: Analyze `setup.py`. It currently uses `checkboxlist_dialog`. Needs to be expanded to handle command-line args or a more complex TUI wizard for the new Install/Uninstall options.
- [ ] **Program Files Access**: Verify permission handling for writing to `C:/Program Files/` from a Python script (likely requires Admin privileges).

### Phase 2 — Modification Strategy
1.  **Execute Config Relocation First**: This is a small, contained task that stabilizes the environment (`~/.storylord`).
2.  **Refactor Schemas**: Move the JSON files (`_schemas.json` -> `schemas.json`, new `registry.json`) before touching the installer, as the installer might need to pack these.
3.  **Implement Setup Overhaul**: This is the largest task.
    - Implement Hash Verification for "Repair".
    - Implement the 5 Uninstall modes.
    - Update Inno Setup script (`installer.iss`) to align with new paths (`Program Files/StoryLord/...`).

### Phase 3 — Implementation Strategy
- **Patch-first**: Apply the Config move immediately.
- **Refactor-first**: For `setup.py`, don't just patch. Re-architect it into a proper CLI/TUI tool (maybe use `click` or `argparse` + `prompt_toolkit`) to handle the complexity of the 5 uninstall modes and repair logic.
