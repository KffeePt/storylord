import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure setup module is findable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from setup.installer import InstallerManager
from setup.utils import INSTALLER_DIR

class TestInstallerManager(unittest.TestCase):
    def setUp(self):
        self.manager = InstallerManager()
        self.downloads_dir = os.path.expanduser("~/Downloads")

    def test_finds_local_versioned_installer_first(self):
        """Should prioritize versioned installer in bin/Installer"""
        local_match = os.path.join(INSTALLER_DIR, "StoryLordSetup_v0.2.0.exe")
        
        # Patching setup.installer.input with create=True ensures we intercept the call
        # even if it wasn't explicitly imported (it looks up in module scope first)
        with patch("setup.installer.glob.glob") as mock_glob, \
             patch("os.path.exists") as mock_exists, \
             patch("subprocess.Popen") as mock_popen, \
             patch("setup.installer.input", create=True, return_value="n") as mock_input:
            
            # Setup mocks
            def exists_side_effect(path):
                if path == INSTALLER_DIR: return True
                if path == self.downloads_dir: return True
                if path.endswith(".exe"): return True
                return False
            mock_exists.side_effect = exists_side_effect
            
            def glob_side_effect(pattern):
                if INSTALLER_DIR in pattern:
                    return [local_match]
                return []
            mock_glob.side_effect = glob_side_effect
            
            # Action
            self.manager.install_app()
            
            # Assert
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            self.assertEqual(args[0], local_match)

    def test_finds_local_legacy_installer_if_no_versioned(self):
        """Should fallback to StoryLordSetup.exe in bin/Installer if no versioned one exists"""
        local_legacy = os.path.join(INSTALLER_DIR, "StoryLordSetup.exe")
        
        with patch("setup.installer.glob.glob") as mock_glob, \
             patch("os.path.exists") as mock_exists, \
             patch("subprocess.Popen") as mock_popen, \
             patch("setup.installer.input", create=True, return_value="n") as mock_input:
             
            def exists_side_effect(path):
                if path == INSTALLER_DIR: return True
                if path == local_legacy: return True
                return False
            mock_exists.side_effect = exists_side_effect
            
            # Glob finds nothing versioned
            mock_glob.return_value = []
            
            # Action
            self.manager.install_app()
            
            # Assert
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            self.assertEqual(args[0], local_legacy)

    def test_downloads_if_missing(self):
        """Should trigger download if no installers found"""
        with patch("setup.installer.glob.glob") as mock_glob, \
             patch("os.path.exists") as mock_exists, \
             patch("subprocess.Popen") as mock_popen, \
             patch("setup.installer.InstallerManager.download_installer") as mock_download:
             
            mock_exists.return_value = True 
            mock_glob.return_value = [] 
            mock_download.return_value = True 
            
            # Action
            self.manager.install_app()
            
            # Assert
            mock_download.assert_called_once()
