# Story Lord Schemas

Story Lord uses a file-based database system where each markdown file represents a database entry. The Metadata Header defined at the top of each file determines how the system indexes and interacts with it.

## The Metadata Header

Each file MUST start with a YAML-like header block. The system scans the first 20 lines of the file for these keys.

```yaml
Title: [Name of the Entry]
Category: [Schema Type]
Version: [x.y]
Description: [Short summary]
```

## Schema Types (Categories)

The `Category` field determines the schema type.

*   **Characters**: Protagonists, Antagonists, NPCs.
*   **Lore**: World history, geography, items.
*   **Canon**: Established facts, timeline events (non-storyboard).
*   **Rules**: Magic systems, physics, game mechanics.
*   **Storyboard**: specialized events (See Storyboard Manual).
*   **Composition**: Drafts and scripts.

## File Organization

Files are stored in `StoryLord/guac/schemas/` (or your active story folder), organized by Category folders. The `Explorer` tool helps manage this structure automatically.
