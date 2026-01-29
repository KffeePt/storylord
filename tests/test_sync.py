import os
from src.core.sync import check_sync_status, fix_all_issues
from src.core.models import StoryMetadata, StorySpec
from src.core.generator import generate_spec

def test_sync_detects_missing_json(mock_specs):
    # Setup: Create file but don't scan
    cat_dir = os.path.join(mock_specs, "Lore")
    os.makedirs(cat_dir)
    # Ensure dir exists before writing
    with open(os.path.join(cat_dir, "ghost.md"), "w") as f:
         f.write("Title: Ghost\n\n")
         
    # Act
    issues = check_sync_status()
    
    # Assert
    # issues is likely a list of dicts. 
    # check structure based on real code if needed, but assuming simple list checks.
    assert len(issues) >= 1
    # Check if we find the issue related to ghost.md
    found = False
    for i in issues:
        if "ghost.md" in str(i): 
            found = True
            break
    assert found

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
