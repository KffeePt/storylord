# Spec 001: Metadata System

## 1. Overview
The Metadata System provides a centralized index of all Story Specifications. It serves as the "Source of Truth" for valid files within the project.

## 2. Components

### A. The Metadata File (`_metadata.json`)
*   **Location**: `specs/_metadata.json`.
*   **Structure**:
    ```json
    {
        "specs": {
            "Category/File.md": {
                "title": "String",
                "category": "String",
                "version": "String",
                "description": "String"
            }
        }
    }
    ```

### B. File Headers
All `.md` files in `specs/` MUST have a header block in the first 20 lines with the format:
```text
Title: My Title
Category: My Category
Version: 0.1
Description: Summary...
```

### C. Synchronization Logic
1.  **Parse**: Read file headers.
2.  **Compare**: Match File Header data against `_metadata.json` data.
3.  **Resolve**: File on Disk is the authority. JSON is updated to match Disk.
4.  **Clean**: Entries in JSON that no longer exist on Disk are removed.
