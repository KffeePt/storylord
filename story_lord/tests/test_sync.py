import os
from story_lord.core.sync import check_sync_status, fix_all_issues
from story_lord.core.generator import generate_spec

def test_sync_detects_missing_json(mock_specs):
    # Setup: Create file but don't scan
    cat_dir = os.path.join(mock_specs, "Lore")
    os.makedirs(cat_dir)
    with open(os.path.join(cat_dir, "ghost.md"), "w") as f:
         f.write("Title: Ghost\n\n")
         
    # Act
    issues = check_sync_status()
    
    # Assert
    assert len(issues) == 1
    assert issues[0]["status"] == "MISSING_IN_JSON"

def test_fix_issues(mock_specs):
    # Setup
    cat_dir = os.path.join(mock_specs, "Lore")
    os.makedirs(cat_dir)
    with open(os.path.join(cat_dir, "ghost.md"), "w") as f:
         f.write("Title: Ghost\n\n")
         
    # Act
    fix_all_issues()
    issues = check_sync_status()
    
    # Assert
    assert len(issues) == 0
