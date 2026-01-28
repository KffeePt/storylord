Title: CLI Interface
Category: Architecture
Version: 0.1
Description: Specification for the AI-friendly Command Line Interface.

## Goals
Provide a robust, scriptable interface for Story Lord that allows AI agents and power users to manage stories and specifications without the TUI.

## Command Structure
The CLI will use a noun-verb structure: `python main.py <noun> <verb> [args]`

### Global Flags
*   `--story <path>`: Explicitly set the story root context. If not provided, defaults to `cwd` or environment variable.
*   `--json`: Output results in JSON format (where applicable) for easy parsing by agents.

### Noun: `story`
*   `list`: List all available stories in the global storage.
*   `create <name>`: Create a new story.
*   `delete <name>`: Delete a story (requires confirmation flag `--yes` or valid interactive input).

### Noun: `spec`
*   `list`: List all specs in the current story (with rudimentary metadata filters).
*   `read <path>`: efficient `cat` equivalent. Outputs the content of a spec file.
*   `create <category> <title>`: Create a new spec file.
    *   `--desc`: Description text.
    *   `--content`: Body content (or pipe from stdin).

### Noun: `tree`
*   Prints a tree of the `specs/` directory.

### Noun: `analyze`
*   Returns stats: Count of specs, categories, missing headers, etc.

## Implementation Details
*   Use `argparse` for zero-dependency parsing.
*   Reuse `core` logic (`metadata.py`, `generator.py`).
*   Ensure all commands support `-h/--help` with verbose descriptions.
