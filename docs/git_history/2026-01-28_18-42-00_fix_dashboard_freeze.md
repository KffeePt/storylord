# Commit: [Pending]

**Author:** AI Assistant (Antigravity)
**Date:** 2026-01-28
**Message:** fix(dashboard): resolve focus freeze and visual regressions

## Description
Resolved critical regression where Dashboard input was frozen and visual highlighting was duplicated.
- **Input Logic**: Replaced specific key bindings in `dashboard.py` with a robust `<any>` handler pattern to bypass binding specificity issues.
- **Focus Management**: Implemented manual "Focus Zone" state (`active_focus_zone`) in `ui/state.py` to decouple visual highlighting from internal PTK focus.
- **Transition Fix**: Updated `ui/screens/launcher.py` to explicitly transfer focus to `dashboard.menu_control` upon story load.
- **Instrumentation**: Added temporary debug header and auto-healing logic to `ui/layout.py` and `ui/app.py` to assist in diagnosing focus traps.
- **Validation**: Restored Gold Frame to Dashboard after confirming it was not the root cause.

## Changes
 story_lord/ui/app.py                |  5 +++++
 story_lord/ui/layout.py             | 45 +++++++++++++++++++++++++++++++++++++--------
 story_lord/ui/screens/dashboard.py  | 74 +++++++++++++++++++++++++++++++++++++-------------------------------------
 story_lord/ui/screens/launcher.py   | 21 ++++++++++-----------
 story_lord/ui/state.py              |  1 +
 legacy/guac_cannon.md               |  3 ++-
 6 files changed, 92 insertions(+), 57 deletions(-)
