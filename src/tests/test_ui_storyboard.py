import pytest
from src.ui.screens import storyboard
from src.core.models import StoryMetadata, StorySpec

def test_storyboard_refresh_data(monkeypatch):
    # Mock metadata loading
    def mock_load():
        m = StoryMetadata()
        m.specs["story_1.md"] = StorySpec(title="S1", category="Storyboard")
        m.specs["other.md"] = StorySpec(title="O1", category="Other")
        m.specs["story_2.md"] = StorySpec(title="S2", category="Storyboard")
        return m
        
    monkeypatch.setattr("src.ui.screens.storyboard.load_all_metadata", mock_load)
    monkeypatch.setattr("src.ui.screens.storyboard.scan_and_sync", lambda: None)
    
    storyboard.refresh_data()
    
    # Check nodes
    nodes = storyboard.sb_state.nodes
    assert len(nodes) == 2
    assert nodes[0][0] == "story_1.md"
    assert nodes[1][0] == "story_2.md"
    
    # Verify sorting (since we mocked dict, key order might vary, but our code sorts by filename)
    # let's assume dict order was stable or random, code should sort.
    # story_1 < story_2
    
def test_storyboard_render_empty():
    storyboard.sb_state.nodes = []
    lines = storyboard.get_timeline_render()
    assert "No Storyboard Nodes Found" in str(lines)
