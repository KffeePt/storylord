import os
from story_lord.core.metadata import scan_and_sync, load_all_metadata, update_file_header

def test_scan_creates_metadata(mock_specs):
    # Setup: Create a file manually
    cat_dir = os.path.join(mock_specs, "Lore")
    os.makedirs(cat_dir)
    with open(os.path.join(cat_dir, "test.md"), "w") as f:
        f.write("Title: Test\nCategory: Lore\nVersion: 1.0\n\nContent")
        
    # Act
    scan_and_sync()
    data = load_all_metadata()
    
    # Assert
    key = "Lore/test.md"
    assert key in data["specs"]
    assert data["specs"][key]["title"] == "Test"
    assert data["specs"][key]["version"] == "1.0"

def test_update_header(mock_specs):
    # Setup
    cat_dir = os.path.join(mock_specs, "Lore")
    os.makedirs(cat_dir)
    fpath = os.path.join(cat_dir, "test.md")
    with open(fpath, "w") as f:
        f.write("Old content")
        
    # Act
    update_file_header(fpath, {"title": "New", "version": "2.0"})
    
    # Assert
    with open(fpath, "r") as f:
        content = f.read()
    assert "Title: New" in content
    assert "Version: 2.0" in content
