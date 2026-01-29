# Commit: e96e6ff

**Author:** Santiago S
**Date:** Wed Jan 28 08:04:56 2026 -0600
**Message:** feat: Initial commit - Story Lord v3 TUI and CLI implementation

## Summary of Changes
This is the initial commit for the fully refactored Story Lord v3 application.

### Core Architecture
*   **Global Storage**: Stories are stored in `~/Documents/StoryLord`. `core/config.py` manages dynamic paths.
*   **Pydantic Models**: `StorySpec` and `StoryMetadata` enforced in `core/models.py`.
*   **CLI**: New `cli.py` module providing `story`, `spec`, `tree`, and `analyze` commands in an AI-friendly format.

### TUI Enhancements
*   **Menu System**: Hierarchical `MenuManager` in `ui/menu.py` with hashmap-based navigation.
*   **Interactive Sidebar**: Focusable sidebar in `layout.py` with `W/S` (Up/Down) and `D` (Enter) navigation.
*   **Gold & Pastel Theme**: Updated `ui/app.py` style registry.
*   **Screens**:
    *   `launcher`: Story selection, creation (with manual naming), and deletion.
    *   `dashboard`: Main menu navigation.
    *   `generator`: Spec creation form.
    *   `explorer`: File tree viewer.
    *   `sync`: Metadata consistency checker.

### User Interaction
*   **WASD Controls**: Added support for WASD keys alongside Arrows.
*   **Input Polish**: Hidden cursors in menus; explicit focus management to prevent "frozen input" states.
