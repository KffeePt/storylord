# Task Summary: setup-modularization

## 1. Project Snapshot
**Context:** Modularization of the build/deploy system for "Story Lord" (Python app).
Refactored `setup.py` and `deploy.py` into a `setup/` package structure to improve maintainability and add features (e.g., auto-downloading installer).

**Key Systems:**
-   **Build System:** `setup/builds.py` (PyInstaller, Inno Setup)
-   **Deploy System:** `setup/deploy.py` (Git tagging, GitHub Releases, PR creation)
-   **TUI/Controller:** `setup/main.py` (prompt_toolkit interface)
-   **Test Runner:** `setup/tests.py` (Unittest wrapper)
-   **Installer Manager:** `setup/installer.py` (Run/Download installer)

**Current Status:**
-   Modularization complete.
-   `bats/` scripts updated to point to new entry points.
-   **Tests Failing:** `python setup.py --test` reports "fatal: tag ... already exists" and failure count (7 errors). This indicates integration tests (likely `test_deploy.py` mocks) might be leaking or not matching the new `setup/deploy.py` logic perfectly, or usage of `git` commands in tests is hitting real repo state.

---

## 2. File-Level Impact Map
*   `setup.py`: **[Heavy Refactor]** converted to wrapper importing `setup.main`.
*   `deploy.py`: **[Deleted]** Logic moved to `setup/deploy.py`.
*   `setup/`: **[New Directory]**
    *   `main.py`: **[New]** Central CLI/TUI logic.
    *   `builds.py`: **[New]** Extracted BuildSystem.
    *   `deploy.py`: **[New]** Extracted Deploy logic.
    *   `tests.py`: **[New]** Extracted TestRunner.
    *   `installer.py`: **[New]** Added download logic.
*   `bats/`: **[New Directory]**
    *   `deploy.bat`, `run.bat`, `setup.bat`: **[Moved/Modified]** Moved from root, updated to `cd ..`.
*   `tests/`: **[Modified]**
    *   `test_deploy.py`: Updated imports (`setup.deploy`).
    *   `test_deployment.py`: Updated imports (`setup.builds`) and converted to `unittest`.
    *   Moved all `src/tests/*` to `tests/`.

---

## 3. Execution Log (Factual Record)
1.  **Refactor**: Created `setup/` package. Moved logic from `setup.py` and `deploy.py`.
2.  **Cleanup**: Deleted root `deploy.py`.
3.  **Bats**: Moved root `.bat` files to `bats/` and corrected paths.
4.  **Tests**: Moved `src/tests` to `tests`. Refactored `test_deploy.py` and `test_deployment.py` to fix `ImportError` caused by modularization.
5.  **Validation**: Ran `python setup.py --test`. Result: `ImportError` fixed, but now failing with logic errors/git tag existence errors.

---

## 4. User Intent Record (Source of Truth)
> "migrate the @[setup.py] to@[setup] and leave setup.py as a wrapper ... make setup the TUI directly"
> "move all @[src/tests] to @[tests] and solve [ImportErrors]"
> "now it says ... fatal: tag 'v0.2.0' already exists ... failing two tests still"

The user wants a clean, modular structure where `setup` is the main entry point for dev tools. They flagged persistent test failures after the move.

---

## 5. Known Failure Patterns
-   **Test Leakage/Mock Issues:** `test_deploy.py` mocks `subprocess`, but output shows "fatal: tag... exists". This suggests potentially the mock is not catching all calls, or the test setup (logic flow) creates a scenario where the tag check (which is mocked to return True for "remote exists") interacts with a `git push` mock that might be logging error output, or `setup/deploy.py` logic has changed such that prompt flow in test is now misaligned.
-   **Unittest vs Pytest:** Mixed usage caused runner issues. Converted `test_deployment.py` to `unittest` which resolved discovery/import, but assertions might be failing.

---

## 6. Separation of Truth Layers
### Facts
-   Codebase is modularized in `setup/`.
-   Tests run via `unittest` now find modules.
-   7 tests are failing.
-   Error message "fatal: tag 'v0.2.0' already exists" appears in test output.

### Observations
-   The "fatal tag exists" message likely comes from `git tag` command execution. Since this is `unit tests`, real git commands should NOT be running. If they are, mocks are incomplete. Or, the mock `side_effect` is printing it / raising it.

### Hypotheses
-   The tests in `test_deploy.py` mock `subprocess.check_call`/`output`. If `setup/deploy.py` uses a slightly different call (e.g. `call` instead of `check_call` or different arguments), the mock won't catch it, and it falls through to the real system (if `deploy` imports `subprocess` directly and we patch `setup.deploy.subprocess`).
-   The "7 errors" might be `ModuleNotFoundError` for `PyQt6` or similar in `test_ui_*.py` files if environment is not set up perfectly in the test runner context, OR logic errors in the refactored deployment tests.

---

## 7. Stability Map
-   **Stable:** `setup/utils.py`, `setup/builds.py` (seem correct locally).
-   **Risky:** `setup/deploy.py` interaction with `git` (logic is complex).
-   **Broken:** Unit tests (`tests/`). Need debugging to fix mocks and assertions.

---

## 8. Antigravity Planning Scaffold

### Phase 1 — Investigation Checklist
-   [ ] Run `python -m unittest tests/test_deploy.py` in isolation to see if "fatal tag" persists.
-   [ ] Run `python -m unittest tests/test_deployment.py` in isolation.
-   [ ] Inspect `test_ui_*.py` errors (the other 5 failures).
-   [ ] Verify `setup/deploy.py` imports. Does it `import subprocess`? Test mocks `setup.deploy.subprocess`. This should work, but check for `from subprocess import ...` usage which would bypass mock.

### Phase 2 — Modeling & Diagnosis Guidance
-   If "fatal tag" prints, a real subprocess call is happening.
-   Check `setup/deploy.py`: logic uses `subprocess.call` in some places and `check_call` in others. Mocks must cover both or `subprocess` module entirely.

### Phase 3 — Implementation Strategy
-   Fix Mocks: Ensure `subprocess` is fully completely mocked in `test_deploy.py`.
-   Fix UI Tests: Ensure they run in headless mode or have deps.
-   Goal: Get `python setup.py --test` to Green.

---

## 9. Compression Mode Behavior
n/a (User provided `<FWUI>`)

## 10. Operational Workflow
- Saved to: `docs/archived_tasks/setup-modularization_20260129T054639.md`
