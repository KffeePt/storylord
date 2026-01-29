import pytest
import os
import sys
import shutil
# Ensure 'src' is in path so 'import ui' works as expected by app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import config

# Fixture to mock SPECS_DIR
@pytest.fixture
def mock_specs(monkeypatch, tmp_path):
    # Create a temp specs dir
    d = tmp_path / "schemas"
    d.mkdir()
    
    # Mock the SPECS_DIR in modules
    # We need to patch where it is import/used.
    # Ideally, core modules should load config.SPECS_DIR, but they import it.
    # If they import contents, patching module.SPECS_DIR works.
    
    # monkeypatch.setattr("src.core.metadata.SCHEMAS_DIR", str(d)) # Removed as it doesn't exist
    # Better: Patch the function get_schemas_dir in config?
    # Or patch the modules that use config. But here we saw they import `get_specs_dir`.
    # Wait, metadata.py imports `get_schemas_dir`.
    # We should patch `src.core.config.get_schemas_dir`?
    # Or if they use a global...
    
    # Original code was patching SPECS_DIR in metadata? 
    # metadata.py does NOT have SPECS_DIR global. It imports get_specs_dir.
    # So the previous conftest was likely patching a variable that didn't exist or I missed `from config import SPECS_DIR`.
    # Let's check metadata.py line 5: `from .config import get_specs_dir`.
    # So patching `src.core.metadata.SPECS_DIR` would only work if it was imported as `from .config import SPECS_DIR`.
    # Ah, I replaced `get_specs_dir` in metadata.py.
    
    # To properly mock this in `conftest`, we should set `core.config._SCHEMAS_DIR` or patch `get_schemas_dir`.
    # Let's try to patch `src.core.config._SCHEMAS_DIR` directly if possible, or just patch the function.
    
    monkeypatch.setattr("src.core.config._SCHEMAS_DIR", str(d))
    monkeypatch.setattr("src.core.config.get_schemas_dir", lambda: str(d))
    
    # Also patch METADATA_FILE
    meta_file = d / "_schemas.json"
    monkeypatch.setattr("src.core.metadata.get_metadata_file", lambda: str(meta_file))
    
    return d
