# Spec 002: Generator Engine

## 1. Overview
The Generator Engine handles the creation of new Story Specification files, ensuring they conform to standard templates and file naming conventions.

## 2. Naming Convention
*   **Sanitization**: Input titles are stripped of non-alphanumeric characters (preserving spaces).
*   **Formatting**: Spaces are replaced with underscores `_`.
*   **Case**: All filenames are lowercase.
*   **Example**: "The Lost City!" -> `the_lost_city.md`

## 3. Idempotency
*   The generator MUST check if a file exists before creating it.
*   It MUST NOT overwrite existing files.

## 4. Templates
Templates are hardcoded strings in `story_lord.core.generator`.
*   **Lore**: Summary + Mechanics sections.
*   **Characters**: Role + Background sections.
*   **Canon**: Arc Description + Key Events.
