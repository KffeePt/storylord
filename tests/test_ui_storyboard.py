import unittest
import sys
import os
# Fix path for src import
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import patch, MagicMock
# Mock pydantic if missing
try:
    import pydantic
except ImportError:
    mock_pyd = MagicMock()
    class MockBase(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    mock_pyd.BaseModel = MockBase
    mock_pyd.Field = MagicMock(return_value="field")
    sys.modules["pydantic"] = mock_pyd

from src.ui.screens import storyboard
from src.core.models import StoryMetadata, StorySpec

class TestStoryboardUI(unittest.TestCase):
    
    @patch('src.ui.screens.storyboard.scan_and_sync')
    @patch('src.ui.screens.storyboard.load_all_metadata')
    def test_storyboard_refresh_data(self, mock_load, mock_scan):
        # Mock metadata loading
        m = StoryMetadata()
        m.specs = {} # Initialize because mock Field returns string
        m.specs["story_1.md"] = StorySpec(title="S1", category="Storyboard")
        m.specs["other.md"] = StorySpec(title="O1", category="Other")
        m.specs["story_2.md"] = StorySpec(title="S2", category="Storyboard")
        
        mock_load.return_value = m
        mock_scan.return_value = None
        
        storyboard.refresh_data()
        
        # Check nodes
        nodes = storyboard.sb_state.nodes
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0][0], "story_1.md")
        self.assertEqual(nodes[1][0], "story_2.md")
        
    def test_storyboard_render_empty(self):
        storyboard.sb_state.nodes = []
        lines = storyboard.get_timeline_render()
        self.assertIn("No Storyboard Nodes Found", str(lines))
