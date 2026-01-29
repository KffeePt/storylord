import os
from src.core import generator
from src.core.models import StorySpec

def test_generate_spec_creates_file(mock_specs):
    # Act
    success, msg = generator.generate_spec("Lore", "My New Spec", "0.1", "Desc")
    
    # Assert
    assert success
    expected_path = os.path.join(mock_specs, "Lore", "my_new_spec.md")
    assert os.path.exists(expected_path)
    
    with open(expected_path, "r") as f:
        content = f.read()
    assert "Title: My New Spec" in content
    assert "Category: Lore" in content

def test_generate_spec_no_overwrite(mock_specs):
    # Setup
    generator.generate_spec("Lore", "Duplicate", "0.1")
    
    # Act
    success, msg = generator.generate_spec("Lore", "Duplicate", "0.2")
    
    # Assert
    assert not success
    assert "already exists" in msg
