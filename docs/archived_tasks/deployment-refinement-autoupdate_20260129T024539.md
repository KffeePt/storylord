# Task Summary: deployment-refinement-autoupdate

## 1. Project Snapshot
**Context**: The user is finalizing the Deployment pipeline for Story Lord. We have successfully overhauled `setup.py` into a system manager (Install/Repair/Uninstall) and created a `deploy.py` script that builds a Portable EXE, an Installer, and releases them to GitHub.

**Current State**:
- `setup.py`: Supports `build` (Portable Dir), `onefile` (Portable EXE), `installer` (Inno Setup). Multi-select menu implemented.
- `deploy.py`: Wraps the build process and uses `gh` CLI to release.
- **Directory Structure**:
    - `bin/Portable`: Directory-based build.
    - `bin/Release`: Single-file portable EXE (`StoryLord-Portable.exe`).
    - `bin/Installer`: Installer EXE (`StoryLordSetup.exe`).

---

## 2. File-Level Impact Map
* `setup.py`: **[Heavy Refactor]**
  * Implemented class-based `BuildSystem`.
  * Added `run_pyinstaller_onefile`, `run_inno_setup`, `install_app`, `uninstall_app`.
  * Renamed output directories (`bin/Portable`).
  * Added logic to inject version into Inno Setup.
  * Added `src` to `sys.path`.
* `deploy.py`: **[New]**
  * Created script to automate the build-and-release pipeline.
  * Added version prompting and config updating.
  * Added GitHub Release creation via `gh` CLI.
* `deploy.bat`: **[New]**
  * Wrapper for `deploy.py`.
* `installer.iss`: **[Moderate Change]**
  * Updated source paths to `bin/Portable`.
  * Updated `AppVersion` to use `{#MyAppVersion}` preprocess definition.
* `story_lord_onefile.spec`: **[New]**
  * Dedicated Spec file for Single-File builds to avoid CLI conflicts.
* `src/core/config.py`: **[Moderate Change]**
  * Separated `APP_DATA_ROOT` (`~/.storylord`) and `STORY_LORD_ROOT` (`~/Documents/StoryLord`).
* `src/ui/screens/dashboard.py`: **[Minor Tweak]**
  * Added "Run Installed App" menu item.

---

## 3. Execution Log (Factual Record)
1.  **Refactored `setup.py`**: Converted to a comprehensive tool. Added multi-select build menu.
2.  **Path Fixes**: Implemented auto-detection for `ISCC.exe` and `sys.executable` for PyInstaller.
3.  **Deployment Script**: Created `deploy.py` that orchestrates the build and uses `gh` to release.
4.  **Version Injection**: Modified `setup.py` to read version from `config.json` and pass it to Inno Setup (`/DMyAppVersion=...`).
5.  **Renaming**: Renamed `bin/Dist` to `bin/Portable` and the single-file output to `StoryLord-Portable.exe`.
6.  **Spec Split**: Created `story_lord_onefile.spec` to solve PyInstaller conflict.

---

## 4. User Intent Record (Source of Truth)

### Raw Instructions
> also if possible add detection for if the user is deploying teh same version of the release file and warn the user that that will overwrite that release version
> also it still just closes immediatly and doesnt display success or failure for build or deploy it should print a report on the success fail state for each of the builds and for the builld->deploy pipeline items
> and also i have to press enter to continue after a build finishes when i select multiple make it instead timeout for 5 seconds and then continue fotr the build scripts while keeping the other timeouts for the success/fail stated of the build->deploy pipeline
> alsoi need an auto update mechanism for the binaries when it runs it will prompt the user to update and restart and it will update and restart with the new version file if it detects the current version is not the version from the releases binary and also for the portable and it will download a the latest portable version to ~/Downloads

---

## 5. Known Failure Patterns
- **PyInstaller Conflict**: Attempting to use `--onefile` CLI flag with a `.spec` file causes an error. **Fix**: Use a dedicated `.spec` file for onefile builds.
- **Import Errors**: Running specific scripts from root without `src` in `sys.path` fails. **Fix**: `sys.path.append(...)` in scripts.
- **Path Confusion**: Users confuse `dist` (PyInstaller default) with our desired `bin/*` structure. **Note**: We manually configure output paths.

---

## 6. Separation of Truth Layers

### Facts
- The user wants a robust deployment pipeline and an auto-update system.
- `gh` CLI is required for deployment.
- The app has two modes: Installed and Portable.

### Observations
- `deploy.py` currently builds blindly; it needs pre-checks (version existence).
- `setup.py` pauses on "Press Enter" which interrupts automated flows.
- Auto-update needs to distinguish between "Installed" (run installer?) and "Portable" (download file).

---

## 7. Stability Map
- **Safe**: `deploy.py` logic updates. `setup.py` UI tweaks (timeouts).
- **Moderate**: Implementing Auto-Update logic in `src/core/updater.py` (New). This involves network requests and potential self-updates.
- **Critical**: `src/main.py` entry point (don't break startup).

---

## 8. Antigravity Planning Scaffold

### Phase 1 — Investigation Checklist
- [ ] Research `gh release view {version}` JSON output to detect existing releases programmatically.
- [ ] Investigate libraries for GitHub API (PyGithub vs raw requests) or stick to `gh` CLI for checking updates? (Note: End users won't have `gh` CLI, so Auto-Update **MUST** use requests/urllib to check GitHub API public endpoints).
- [ ] Determine how to prompt user in TUI vs CLI for updates.

### Phase 2 — Modeling & Diagnosis Guidance
- **Deploy Warning**: In `deploy.py`, Step 0 should be "Check Release Existence".
- **Deploy Reporting**: Create a `Report` class or dict that collects status of (OneFile, DirBuild, Installer, Upload) and prints a summary.
- **Auto Update**:
    - **UpdateChecker**: Runs on startup (threaded?). Checks `https://api.github.com/repos/{owner}/{repo}/releases/latest`.
    - **Logic**:
        - If `latest_tag != current_version`:
            - If `frozen` (compiled): Prompt to Update.
            - If Installed (check reg keys or path?): Download `StoryLordSetup.exe` -> Run.
            - If Portable: Download `StoryLord-Portable.exe` -> `~/Downloads`.

### Phase 3 — Implementation Strategy
1.  **Refine `deploy.py`**:
    - Add pre-check for existing version.
    - Collect step results.
    - Print summary table.
    - Ensure window lingers (partially done).
2.  **Refine `setup.py`**:
    - Replace `input("Press Enter...")` in build methods with a 5-second countdown if successful. Keep explicit wait on error.
3.  **Implement Auto-Update**:
    - Create `src/core/updater.py`.
    - Integrate into `main.py` startup sequence (or Dashboard "Check for Updates").
    - **Requirement**: "When it runs it will prompt... update and restart".
