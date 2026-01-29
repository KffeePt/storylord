# Task Summary: installer-debugging

## 1. Project Snapshot
- **Architecture Overview**: Python TUI application (`StoryLord`) with a modular setup system in `setup/`. Deployment involves PyInstaller for builds and Inno Setup for Windows installers.
- **Key Systems**:
  - `setup/`: Custom build/deploy/test package.
  - `installer.iss`: Inno Setup script.
  - `setup/installer.py`: Local installer management (search/download).
- **Current Status**: Modularization is complete and documented. Unit tests for `installer.py` exist. However, the Installer logic for "Update/Repair" is not behaving as the user expects. The user provided a specific guide to correct this.

---

## 2. File-Level Impact Map
* `installer.iss`: **[Major Fix Required]**
  * Change: Needs rewrite based on user guide (AppId, Privileges, Files flags).
* `setup/builds.py`: **[Review]**
  * Change: Verify matches user's PyInstaller command requirements (console mode).
* `setup/installer.py`: **[Stable]**
  * Change: Recently patched for search logic (verified by tests), but may need adjustments if filenames change.
* `tests/test_installer_manager.py`: **[New]**
  * Change: Added to verify `installer.py`.
* `docs/dev/setup_system.md`: **[New]**
  * Change: Created to document the system.

---

## 3. Execution Log (Factual Record)
- **Objective**: Fix installer "Maintenance Mode", customize filenames, and improve search logic.
- **Actions**:
  - Modularized `setup.py` into `setup/` package.
  - Updated `installer.iss` with `AppId` and Registry checks (HKLM/HKCU).
  - Updated `setup/installer.py` to search local `bin/Installer` and `~/Downloads`.
  - Added unit tests for `installer.py` (overcoming input mocking issues).
  - Created developer documentation.
- **Outcome**: The code logic seems correct for "standard" Inno Setup, but user reports it's "not working" as intended regarding version detection and repair options. User provided a specific "Golden Path" guide to solve this.

---

## 4. User Intent Record (Source of Truth)

### Raw Instructions (Sanitized)
> ok so its not working still below is a guide on how to do it correctly understand it and implement a fix
>
> **Phase 1: Prepare the Python Executable**
> - Install PyInstaller.
> - Build EXE: `pyinstaller --onefile --name "StoryLord" main.py` (Crucial: Do not use --noconsole).
>
> **Phase 2: The Master Inno Setup Script**
> - Copy provided code to `installer.iss`.
> - **Update**: Uses fixed `AppId` to detect old versions and overwrite.
> - **Repair**: Sets `Flags: ignoreversion` to overwrite/fix broken files.
> - **Uninstall**: Standard uninstaller + cleanup of `.log` and `.tmp`.
> - **TUI Handling**: Ensures app launches in visible console.
> - **Privileges**: Requests `admin`.
>
> **Phase 3: Requirements Implementation**
> - **Update**: Matching `AppId` allows Inno to detect/overwrite old folders.
> - **Repair**: `ignoreversion` flag acts as repair mechanism (re-running installer fixes corrupt files).
> - **Uninstall**: Clean up extra files.

---

## 5. Known Failure Patterns
- **Maintenance Mode Detection**: Previous attempts using Registry checks (`UninstallString`) were flaky or "hardcoded". User suggests relying on Inno's native `AppId` detection + `ignoreversion` for "Repair" behavior instead of manual "Maintenance Mode" pages.
- **Version Hardcoding**: User noted "it says 0.2.0 meaning its hardcoded". Need to ensure the Inno script receives the dynamic version properly (currently passed via `/DMyAppVersion` in `builds.py`, but user wants to verify this).

---

## 6. Separation of Truth Layers
### Facts
- User provided a specific Inno Setup script template.
- User wants `AppId={{A1B2C3D4-E5F6-7890-1234-56789ABCDEF0}` (or a generated unique one) used consistently.
- User wants `Flags: ignoreversion` used for the EXE.

### Observations
- The user's guide suggests `PrivilegesRequired=admin`, whereas we previously set `lowest`. This is a conflict to resolve (Admin allows Program Files install, Lowest is safer/easier for updates).
- The user's guide uses `DefaultDirName={autopf}\{#MyAppName}`, implying Program Files.

### Hypotheses
- The user prefers "Re-run installer to repair" (via `ignoreversion`) over a dedicated "Repair" button in a custom wizard page.

---

## 7. Stability Map
- **Safe**: `setup/installer.py` (Search logic is generic).
- **Volatile**: `installer.iss` (Needs total rewrite based on guide).
- **Volatile**: `setup/builds.py` (Need to align PyInstaller arguments with Phase 1).

---

## 8. Antigravity Planning Scaffold

### Phase 1 — Investigation Checklist
- [ ] Read `setup/builds.py`: Does `run_pyinstaller` match `pyinstaller --onefile --name "StoryLord" main.py`?
  - Note: Current implementation uses `story_lord.spec`. Check if spec includes `console=True`.
- [ ] Read `installer.iss`: Compare current script with User's "Master Script".

### Phase 2 — Modeling & Diagnosis Guidance
- **Design Drift**: We were building a "Custom Maintenance Page". User wants standard Inno behavior where "Install over existing" = "Update/Repair".
- **Architecture**: Move away from manual registry checks if `AppId` handles it natively.

### Phase 3 — Implementation Strategy
1.  **PyInstaller**: Ensure `main.py` is the entry point (or `src/main.py`) and console is enabled.
2.  **Inno Setup**:
    - Replace `installer.iss` content with User's provided template.
    - **Crucial**: Generate a *real* unique GUID for `AppId` (do not use the placeholder `{{A1B2...`).
    - Update `Source` path in `[Files]` to match actual output (`bin/Dist` or `bin/Portable`).
    - Inject `MyAppVersion` dynamically via CLI defines (already supported in `builds.py`, just ensure strict adherence).
3.  **Verify**: Run loop.
