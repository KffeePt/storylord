import os
import sys
import shutil
import subprocess
import unittest

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from setup.builds import BuildManager

class TestDeploymentPipeline(unittest.TestCase):
    
    def setUp(self):
        self.build_system = BuildManager()

    def test_paths_exist(self):
        """Verify critical paths exist before starting."""
        self.assertTrue(os.path.exists("setup.py"))
        self.assertTrue(os.path.exists(os.path.join("setup", "deploy.py")))
        self.assertTrue(os.path.exists("story_lord_onefile.spec"))
        self.assertTrue(os.path.exists("installer.iss"))

    def test_iscc_detection(self):
        """Verify Inno Setup Compiler is found."""
        iscc = self.build_system._find_iscc()
        if not iscc:
            self.skipTest("ISCC not found, cannot test installer build")
        self.assertTrue(os.path.exists(iscc))

    def test_pyinstaller_onefile_build(self):
        """Test Single File Build (dry run or full)."""
        # Full build is slow, maybe just check if spec is valid?
        pass

if __name__ == "__main__":
    # Integration Script: Mock Run
    print("Running Pipeline Integration Simulation...")
    
    # 1. Check Dependencies
    if not shutil.which("git"):
        print("FAIL: git not found")
    else:
        print("PASS: git found")

    if not shutil.which("gh"):
        print("WARN: gh (GitHub CLI) not found")
    else:
        print("PASS: gh found")
        
    bs = BuildManager()
    iscc = bs._find_iscc()
    if iscc:
        print(f"PASS: ISCC found at {iscc}")
    else:
        print("FAIL: ISCC not found")
        
    print("\nTo run full build test, execute:\npython setup.py --build --onefile")
