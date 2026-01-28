import pytest
import os
import shutil
from story_lord.core import config

# Fixture to mock SPECS_DIR
@pytest.fixture
def mock_specs(monkeypatch, tmp_path):
    # Create a temp specs dir
    d = tmp_path / "specs"
    d.mkdir()
    
    # Mock the SPECS_DIR in modules
    # We need to patch where it is import/used.
    # Ideally, core modules should load config.SPECS_DIR, but they import it.
    # If they import contents, patching module.SPECS_DIR works.
    
    monkeypatch.setattr("story_lord.core.metadata.SPECS_DIR", str(d))
    monkeypatch.setattr("story_lord.core.generator.SPECS_DIR", str(d))
    monkeypatch.setattr("story_lord.core.sync.SPECS_DIR", str(d))
    
    # Also patch METADATA_FILE
    meta_file = d / "_metadata.json"
    monkeypatch.setattr("story_lord.core.metadata.METADATA_FILE", str(meta_file))
    
    return d
