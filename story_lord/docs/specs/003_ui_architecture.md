# Spec 003: UI Architecture

## 1. Overview
The User Interface is a Terminal User Interface (TUI) built on `prompt_toolkit`. It uses a Single Page Application (SPA) pattern.

## 2. Layout
*   **Header**: Status bar and Version info. Persistent.
*   **Sidebar**: Navigation menu. Highlight shows active screen.
*   **Content Area**: Dynamic container that swaps content based on `AppState.active_screen`.

## 3. State Management
*   **Singleton**: `story_lord.ui.state.state` holds all mutable UI state.
*   **Fields**:
    *   `active_screen`: String Enum (DASHBOARD, GENERATOR, EXPLORER, SYNC).
    *   `status_message`: String for feedback.
    *   `exp_files`: List of files for Explorer.
    *   `sync_issues`: List of issues for Sync Dashboard.

## 4. Navigation
*   **Function Keys**: Global bindings (F1-F4) allow instant switching between screens.
*   **Exit**: `Ctrl+C` globally, or `Q` in Dashboard.
