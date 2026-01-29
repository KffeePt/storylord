# Task Summary: installer-wrapping-up

## 1. Project Snapshot
- **Architecture Overview**: Python TUI (StoryLord) with Inno Setup installer. Unique build system in `setup/`.
- **Key Systems**:
  - `installer.iss`: Inno Setup script (recently fixed for crash/singleton).
  - `src/core/config.py`: Versioning logic (needs Git tag integration).
  - `src/ui/`: TUI layout (needs spacing adjustments).
  - `setup/main.py`: Build system TUI (needs animation polish).
- **Current Status**: Installer build is stable. Crash on launch fixed. Singleton installer lock implemented. Nuke Binaries option added. Auto-wait implemented.
- **Pending Tasks**:
  1.  **Versioning**: Installer uses hardcoded `v0.2.0` instead of local Git tag.
  2.  **UI Polish**: "Unbalanced" spacing on the right side of the TUI.
  3.  **Process Detection**: Installer needs to detect if *Story Lord* (the app) is running and prompt to close it.
  4.  **Setup Aesthetics**: Animate Setup TUI background (Rainbow Sine Wave) and hide the cursor.

---

## 2. File-Level Impact Map
* `installer.iss`: **[Minor Tweak]**
  * Change: Add `AppMutex` to detect running application instances.
* `src/core/config.py` (or version logic): **[Feature]**
  * Change: Implement dynamic Git tag retrieval for `get_app_version`.
* `src/ui/screens/dashboard.py`: **[Style Fix]**
  * Change: Adjust right margin/padding to balance the TUI border.
* `setup/main.py`: **[Polish]**
  * Change: Implement background animation loop and cursor hiding code (`\033[?25l`).
* `src/core/instance_manager.py`: **[Read-Only]**
  * Action: Identify the specific Mutex name used by the app to use in `installer.iss`.

---

## 3. Execution Log (Factual Record)
- **Objective**: Debug Installer (Crash, Duplicates, Locks).
- **Actions**:
  - Modified `story_lord.spec`: Fixed `ModuleNotFoundError`.
  - Modified `installer.iss`: Reverted `AppId`, added `SetupMutex`, added `runasoriginaluser`, fixed `userprofile` constant.
  - Added "Nuke Binaries" option to `setup/main.py`.
  - **Implemented Auto-Wait**: Replaced manual `input()` blocking with 15s automatic countdown in `setup/main.py` and `setup/deploy.py`.
- **Outcome**: Installer builds successfully (`StoryLordSetup_Fixed.exe`). Build system now flows automatically.

---

## 4. User Intent Record (Source of Truth)

### Raw Instructions (Sanitized)
> 1. Installer name should show the git tag.
> 2. TUI has unbalanced spacing on the rightmost side.
> 3. Add detection for when story lord is itself running (prompt to close).
> 4. **New**: Animate the background color to a sin wave that alternate a rainbow color animation to the blue background of the setup TUI.
> 5. **New**: Hide the cursor because it is an ugly looking gray square hovering over the selected option.

---

## 5. Known Failure Patterns
- **Zombie Process Check**: `StoryLordSetup_v0.2.0.tmp` (PID 6596) caused file locks. Nuke Binaries mitigates this.
- **Uninstall Error**: Uses `GetEnv('USERPROFILE')` instead of `ExpandConstant`.

---

## 6. Separation of Truth Layers
### Facts
- The installer name is currently `StoryLordSetup_v0.2.0.exe`.
- User wants standard Git tags utilized.
- Setup TUI is built with `prompt_toolkit` or similar (uses `radiolist_dialog`). Note: `setup/main.py` uses `prompt_toolkit` shortcuts. Achieving "Rainbow Sine Wave" background in `radiolist_dialog` might require custom renderer or full `Application` layout instead of simple shortcuts.

### Observations
- `setup/main.py` imports `radiolist_dialog`. These shortcuts are modal and block. Animating the background *behind* a modal dialog in a terminal requires threading or switching to a full full-screen application.

---

## 7. Stability Map
- **Safe**: `installer.iss`.
- **Volatile**: `setup/main.py` (Switching from simple dialogs to animated backgrounds is a significant complexity jump).

---

## 8. Antigravity Planning Scaffold

### Phase 1 — Investigation Checklist
- [ ] **Mutex Name**: Check `src/core/instance_manager.py`.
- [ ] **Version Logic**: Check git tag availability.
- [ ] **Setup TUI**: Investigate `setup/main.py` imports. Can `radiolist_dialog` support background tasks/animations? (Likely not easily; might need full `Application` class).

### Phase 2 — Modeling
- **App Detection**: `AppMutex={Name}`.
- **Setup Animation**:
  - *Option A*: Simple ANSI color cycling in a separate thread (risky vs TUI library).
  - *Option B*: Refactor `setup/main.py` to use `prompt_toolkit.layout` explicitly instead of `shortcuts` to allow custom background rendering.
- **Cursor**: `sys.stdout.write("\033[?25l")` (standard VT100).

### Phase 3 — Implementation Strategy
1.  **Modify `installer.iss`**: Add `AppMutex`.
2.  **Modify `core/config.py`**: Add dynamic git tag fetching.
3.  **Modify `ui/screens/dashboard.py`**: Fix spacing.
4.  **Refactor `setup/main.py`**:
    - Hide cursor on start.
    - Implement background animation (requires careful design to not break input).
5.  **Verify**: Build -> Test.
