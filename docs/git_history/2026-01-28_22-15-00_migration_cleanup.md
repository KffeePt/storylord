# Commit: [Pending]

**Author:** AI Assistant (Antigravity)
**Date:** 2026-01-28
**Message:** chores(migration): migrate legacy content and refine build tools

## Description
Performed final cleanup and migration of legacy content into the proper Story Lord schema structure. Enhanced the build tool for better usability.
- **Migration**: Moved content from `legacy/` to `StoryLord/guac/schemas/{Characters,Rules,Canon}`.
- **Cleanup**: Removed `legacy/` directory.
- **Build Tool**: Updated `setup.py` to support multiple task selection (Checkbox list).
- **Config**: Added `.pytest_cache` to `.gitignore`.

## Changes
 setup.py           | Updated (Multi-select)
 .gitignore         | Updated
 legacy/            | Deleted
