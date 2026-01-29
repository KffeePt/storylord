# Story Lord Architecture Overview

## Modular Design
Story Lord v3 follows a strict separation of concerns:

```
[ UI Layer ]  <-- Call -->  [ Core Layer ]
(TUI / Views)               (Files / Logic)
```

## Core Layer (`story_lord/core`)
*   **metadata.py**: The brain. Reads/Writes `_metadata.json` and parses file headers.
*   **generator.py**: The factory. Creates new `.md` files from templates.
*   **sync.py**: The auditor. Compares Disk state vs Metadata state.
*   **config.py**: Constants (Categories, Paths).

## UI Layer (`story_lord/ui`)
*   **app.py**: Application entry point. Registers screens.
*   **state.py**: Singleton state container.
*   **layout.py**: Defines the visual grid (Header, Sidebar, Body).
*   **screens/*.py**: Individual screen logic (Dashboard, Generator, etc).

## Data Flow
1.  **User** interacts with UI (e.g., Press F9 in Generator).
2.  **UI** calls `core.generator.generate_spec()`.
3.  **Core** writes file to Disk and updates Header.
4.  **UI** updates `state.status_message` with result.
