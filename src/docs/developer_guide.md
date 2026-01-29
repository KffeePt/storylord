# Developer Guide

## Setup
1.  Install dependencies: `pip install -r requirements.txt`.
2.  Run App: `.\run_story_lord.bat`.

## Running Tests
Tests use `pytest`. 
```bash
pytest story_lord/tests
```

## Adding a New Screen
1.  Create `story_lord/ui/screens/myscreen.py`.
2.  Define a `layout` object (prompt_toolkit container).
3.  Register it in `story_lord/ui/app.py`:
    ```python
    SCREENS["MYSCREEN"] = myscreen.layout
    ```
4.  Add a Key Binding to switch to it (e.g., F5).

## Adding a New Command
1.  Implement logic in `story_lord/core/`.
2.  Import it in your UI screen.
3.  Trigger it via key binding or button handler.
