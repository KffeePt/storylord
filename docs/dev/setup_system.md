# Story Lord Setup System Documentation

This document explains the modular build, deployment, and testing system located in the `setup/` directory.

## Directory Structure

Running `python setup.py` delegates to `setup/main.py`.

- **`setup/main.py`**: Entry point. Handles CLI arguments (`--build`, `--test`, etc.) and the TUI menu.
- **`setup/builds.py`**: Logic for building the application:
  - `run_pyinstaller()`: Builds directory-based executable (`bin/Dist`).
  - `run_inno_setup()`: Builds the Windows Installer (`bin/Installer`).
  - Generates `manifest.json` for integrity checks.
- **`setup/deploy.py`**: Logic for GitHub releases and PRs.
  - Checks for uncommitted changes.
  - Version bumping.
  - Pushing tags to trigger GitHub Actions (CI/CD).
  - Creating Pull Requests via `gh` CLI.
- **`setup/installer.py`**: Manages local installation.
  - Finds existing installers (`bin/Installer` or `~/Downloads`).
  - Downloads updates from GitHub Releases if missing.
  - Launches the installer or uninstaller.
- **`setup/tests.py`**: Custom test runner wrapper around `unittest`.

## Common Commands

### Building
```bash
# Build everything (Portable + Installer)
python setup.py --build-all

# Build only the Installer (requires Inno Setup)
python setup.py --build --installer
```

### Installation
```bash
# Run the installer (checks local build first, then downloads latest)
python setup.py --install
```

### Testing
```bash
# Run all unit tests
python setup.py --test

# Run specific test file
python -m unittest tests/test_deploy.py
```

## Writing Tests

We use `unittest` for the test suite. All tests must be located in the `tests/` directory.

### Auto-Discovery Rules
1. Files must be named `test_*.py`.
2. Classes must inherit from `unittest.TestCase`.
3. Methods must start with `test_`.

### Example Test
```python
import unittest
from setup.utils import Colors

class TestUtils(unittest.TestCase):
    def test_colors_exist(self):
        self.assertTrue(hasattr(Colors, 'GREEN'))
```

### Mocking Guidelines
Since the setup scripts interact heavily with the filesystem and `subprocess` (Git, PyInstaller), you **MUST** mock these interactions to avoid accidental side effects.

```python
from unittest.mock import patch, MagicMock

@patch("subprocess.check_call")
def test_git_push(self, mock_call):
    # Action
    my_function_calling_git()
    
    # Assertion
    mock_call.assert_called_with(["git", "push"])
```

## Deployment Workflow

1. **Verify**: Ensure all tests pass (`python setup.py --test`).
2. **Commit**: Save your changes.
3. **Deploy**:
   ```bash
   python setup.py --deploy
   ```
   - This will prompt for a version tag (e.g., `v0.2.1`).
   - Updates `src/core/_version.py`.
   - Tags the commit and pushes to `origin`.
   - **GitHub Actions** detects the tag and builds the Release automatically.

## Installer Logic
The installer (`installer.iss`) is compiled by Inno Setup.
- It detects if the app is already installed (via Registry checks).
- If installed, it offers **Maintenance Mode**:
  - **Update/Repair**: Re-installs over the existing version.
  - **Uninstall**: Runs the uninstaller.
- **Uninstaller**: Can optionally remove Configuration (`.storylord`) and Story Data (`Documents/StoryLord`).
