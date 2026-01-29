# Versioning & Checkpoints

Story Lord uses a strictly monotonic "Checkpoint" versioning system. This ensures that every meaningful change is captured as a distinct step forward in the application's evolution.

## The Checkpoint Philosophy

> "Checkpoints for a full version increase are composed of those previous increases."

Every commit to the codebase is treated as a **Checkpoint**. A version number isn't just a label; it's a coordinate in the development timeline.

## Stability Stages & Increment Rules

*   **Alpha (Checkpoint) [Order 0.0.1]**
    *   **Trigger**: `/checkpoint` workflow (default).
    *   **Action**: `+0.0.1` (Patch).
    *   **Format**: `vX.Y.Z_alpha`
    *   **Example**: `v0.0.1_alpha` -> `v0.0.2_alpha`

*   **Beta (Commit) [Order 0.1]**
    *   **Trigger**: `/commit` workflow (default).
    *   **Action**: `+0.1.0` (Minor).
    *   **Format**: `vX.Y.Z_beta`
    *   **Example**: `v0.0.2_alpha` -> `v0.1.0_beta`

*   **Prod (Release)**
    *   **Trigger**: Explicit Manual Release or FWUI Override.
    *   **Format**: `vX.Y.Z_prod` (or plain `vX.Y.Z` if desired).
    *   **Example**: `v0.9.0_beta` -> `v1.0.0_prod`

## Manual Overrides (Priority)

The standard automated flow is **Beta** for commits and **Alpha** for checkpoints. However, you can strictly valid override this behavior using `<FWUI>` tags in your prompt.

*   **Strict Override**: If you provide a specific version string in `<FWUI>` tags, the system will FORCE that version, ignoring all other logic.
    *   *Prompt*: `<FWUI>Set version to v2.0.0_prod</FWUI>`
    *   *Result*: `v2.0.0_prod`
*   **Missing Tags**: If `<FWUI>` tags are empty, the system defaults to the standard workflow (Alpha/Beta).

## Automated Workflow

The versioning process is automated via the `commit` workflow:
1.  The system analyzes the commit type (`feat` vs `fix`).
2.  It automatically calculates the next version number.
3.  The new version is stored in `config/config.json`.
4.  The application Title Bar updates to reflect the new version.

## Manual Overrides

In rare cases, you may force a specific version or skip bumping by providing `<FWUI>` tags in your commit instructions.
