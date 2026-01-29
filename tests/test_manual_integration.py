import sys
import os
import json
import pytest
from core.version_manager import VersionManager
from ui.screens.settings import SettingsState

@pytest.fixture
def config_path(tmp_path):
    # Use Pytest's tmp_path fixture for isolated config
    path = tmp_path / "config.json"
    return str(path)

def test_version_manager_initialization(config_path):
    vm = VersionManager(config_path)
    assert vm.get_version() == "v0.0.1_alpha", f"Initial version mismatch: {vm.get_version()}"

def test_version_bump_patch(config_path):
    vm = VersionManager(config_path)
    vm.bump_patch() # Default bump patch is Alpha
    assert vm.get_version() == "v0.0.2_alpha", f"Patch bump failed: {vm.get_version()}"
    
    # Validation Persistence
    vm2 = VersionManager(config_path)
    assert vm2.get_version() == "v0.0.2_alpha", "Persistence failed on reload"

def test_version_bump_minor(config_path):
    vm = VersionManager(config_path)
    vm.bump_minor() # Default bump minor is Beta
    assert vm.get_version() == "v0.1.0_beta", f"Minor bump failed: {vm.get_version()}"

def test_manual_registry_loading():
    s = SettingsState()
    s.load_registry()
    
    # Assertions rely on actual manual.json being present in docs/manual
    # This integration test expects the real environment
    assert len(s.manual_nodes) > 0, "No manual nodes loaded"
    
    first = s.manual_nodes[0]
    assert "title" in first
    assert "desc" in first
    assert "file" in first

def test_manual_viewer_loading():
    s = SettingsState()
    s.load_registry()
    
    # Find a file node
    node = next((n for n in s.manual_nodes if n["file"]), None)
    assert node is not None, "No file node found in registry"
    
    s.load_viewer_content(node["file"])
    assert len(s.viewer_content) > 0, "Viewer content empty"
    assert not s.viewer_content[0].startswith("Error"), f"Viewer loaded error: {s.viewer_content[0]}"
