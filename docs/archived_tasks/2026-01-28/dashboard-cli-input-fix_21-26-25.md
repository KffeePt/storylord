# Task Summary: dashboard-cli-input-fix

## 1. File Context
*   `story_lord/ui/screens/dashboard.py`: **[Magnitude: Heavy Refactor]**
    *   *Change:* Implemented robust input handling using `<any>` pattern to fix freeze; restored Gold Frame.
*   `story_lord/ui/screens/explorer.py`: **[Magnitude: Heavy Refactor]**
    *   *Change:* Overhauled to support Fixed Categories (Storyboard first), file counts, and Drill-down navigation.
*   `story_lord/ui/screens/launcher.py`: **[Magnitude: Heavy Refactor]**
    *   *Change:* Fixed focus transition to explicitly target Sidebar on load; fixed initial focus.
*   `story_lord/ui/layout.py`: **[Magnitude: Tweak]**
    *   *Change:* Added Debug Header toggle and auto-healing focus logic.
*   `story_lord/ui/app.py`: **[Magnitude: Tweak]**
    *   *Change:* Added Global keys `Q` (Exit) and `F3` (Debug Toggle).
*   `story_lord/ui/state.py`: **[Magnitude: Tweak]**
    *   *Change:* Added `active_focus_zone` and `show_debug` flags.
*   `docs/git_history/*`: **[Magnitude: New Files]**
    *   *Change:* Detailed git history documentation for commits.

## 2. Execution Log
*   **Main Task**: Resolve Critical Dashboard Freeze and Visual Regressions.
*   **Secondary Tasks & Side Effects**:
    *   Implemented "Manual Focus Zone" state to decouple visuals from PTK internal focus.
    *   Renamed `Episodes` directory to `Storyboard`.
    *   Standardized Input Handling across Dashboard and Launcher.
    *   Verified fixes for Double Highlighting and "Ghost" Inputs.
    *   Implemented Global Quit (Q) and Debug View (F3).

## 3. Historic Feedback
*   **Previous Feedback**: "Input frozen", "Two highlighted items", "Make initial focus on Dashboard", "Explore structure overhaul".
*   **Status**: **Resolved**.

## 4. Current User Feedback & Next Steps
*(Based on input following /compress)*

### User Instructions (Sanitized)
> Make the Storyboard a special folder. This will be the central planning timeline UI. Instead of the normal folder view, it should be a fullscreen UI for viewing nodes and arranging them in a chain sequence, sort of like a pedal board effect chaining UI. In this case, it is a Timeline of events by writing a node and referencing other nodes and other files in Canon, Characters, Composition, Lore, Rules.
>
> Make the Storyboard option highlighted in a different color to indicate its difference visually.
>
> Make it so user can restart the CLI with F5.
>
> Make the debug active with F3 not be on by default.

### Implementation Plan Draft
*The user wants to elevate "Storyboard" from a simple file list to a complex "Timeline Node Editor" and add remaining CLI polish.*

**Current State:**
- `explorer.py` currently treats "Storyboard" as just the first category in a list.
- Debug mode defaults to `True` in `state.py`.
- No F5 binding exists.

**Reasoning:**
- A "Node/Timeline Editor" in TUI requires a dedicated screen (`storyboard_ui.py`) with specialized rendering logic (not just a list of files). It needs to visualize connections/sequence.
- We need to intercept the navigation: When user selects "Storyboard" in Dashboard/Explorer, it shouldn't just show a file list, it should launch this new UI.

**Action Plan:**
- [Step 1] **Polish**: Set `state.show_debug = False`. Add `kb.add('f5')` in `app.py` to trigger a python restart (using `os.execv`).
- [Step 2] **Visual Distinction**: In `dashboard.py` or `explorer.py`, apply a distinct style (e.g., `class:special-storyboard`) to the "Storyboard" label.
- [Step 3] **Storyboard UI Foundation**:
    - Create `ui/screens/storyboard.py`.
    - Design a "Canvas" or "Timeline" view.
    - Implement a data structure for "Event Nodes" (Time, Description, References).
- [Step 4] **Integration**: Update Navigation to route to the new Storyboard Screen when selected.
