import unittest
from unittest.mock import patch, MagicMock
import sys
import subprocess
import os

# Ensure we can import from root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from setup import deploy
from setup.deploy import DeployManager

class TestDeployScript(unittest.TestCase):
    
    def setUp(self):
        # Silence print statements
        self.patcher = patch('builtins.print')
        self.mock_print = self.patcher.start()
        self.dm = DeployManager()
        
    def tearDown(self):
        self.patcher.stop()

    @patch('setup.deploy.subprocess.check_output')
    def test_can_push_to_main_true(self, mock_check_output):
        mock_check_output.return_value = b"WRITE\n"
        self.assertTrue(deploy.can_push_to_main())

    @patch('setup.deploy.subprocess.check_output')
    def test_can_push_to_main_false(self, mock_check_output):
        mock_check_output.return_value = b"READ\n"
        self.assertFalse(deploy.can_push_to_main())

    @patch('setup.deploy.subprocess.check_output')
    def test_check_branch_is_main(self, mock_check_output):
        mock_check_output.return_value = b"main\n"
        self.assertTrue(deploy.check_branch_is_main())
        
        mock_check_output.return_value = b"feature/test\n"
        self.assertFalse(deploy.check_branch_is_main())

    @patch('setup.deploy.subprocess.check_call')
    @patch('setup.deploy.subprocess.check_output')
    @patch('builtins.input')
    def test_submit_pull_request_flow(self, mock_input, mock_check_output, mock_check_call):
        # State to track if checkout happened
        self.branch_state = "main"

        def side_effect_check_output(args, **kwargs):
            cmd = " ".join(args)
            if "git branch --show-current" in cmd:
                return self.branch_state.encode('utf-8')
            if "git status" in cmd:
                return b"M  file.py\n"
            if "gh repo view" in cmd:
                return b"WRITE\n"
            return b""
            
        def side_effect_check_call(args, **kwargs):
            cmd = " ".join(args)
            if "git checkout -b" in cmd:
                # Extract branch name and switch state
                self.branch_state = args[3] # git checkout -b <name>
            return 0

        mock_check_output.side_effect = side_effect_check_output
        mock_check_call.side_effect = side_effect_check_call
        
        # User inputs:
        # 1. Branch Name -> "feat/new-thing"
        # 2. Commit Msg -> "Added feature"
        mock_input.side_effect = ["feat/new-thing", "Added feature"]
        
        self.dm.submit_pull_request("1.0.0")
        
        # Assertions
        # 1. Checked out new branch
        mock_check_call.assert_any_call(["git", "checkout", "-b", "feat/new-thing"])
        # 2. Pushed correct branch (the one we switched to)
        mock_check_call.assert_any_call(["git", "push", "-u", "origin", "feat/new-thing"])
        # 3. Created PR
        mock_check_call.assert_any_call(["gh", "pr", "create"])

    @patch('setup.deploy.tag_exists_remote')
    @patch('setup.deploy.subprocess.call')
    @patch('setup.deploy.subprocess.check_call')
    @patch('builtins.input')
    def test_deploy_release_trigger_logic(self, mock_input, mock_check_call, mock_call, mock_tag_exists_remote):
        # Mocks
        mock_tag_exists_remote.return_value = True
        
        # We need to mock can_push_to_main to return True so we don't get stuck in the permission warning check
        with patch('setup.deploy.can_push_to_main', return_value=True):
            # And mock check_output for git status check
             with patch('setup.deploy.subprocess.check_output', return_value=b""):
                 # Inputs:
                 # 1. Tag Version -> "0.2.0"
                 # 2. Force re-trigger? -> "y"
                 # (Note: "Remote build proceed?" is skipped if we don't return early? 
                 # Wait, deploy_release prompts: "Proceed? (Y/n)". So we need that too.)
                 
                 # Sequence in deploy_release:
                 # 1. Tag Input (v version) -> "0.2.0"
                 # 2. (Optional) Commit changes? (We mocked status clean, so skipped)
                 # 3. (Optional) Overwrite release (We didn't mock gh installed check fully, 
                 # passing gh_installed=True means it checks 'gh release view'. 
                 # Let's mock check_call to raise error for 'gh release view' so it thinks it doesn't exist)
                 
                 # 4. "Proceed? (Y/n)" -> "y"
                 # 5. "Force re-trigger CI? (Y/n)" -> "y"
                 
                 # Adjust input side effects based on new Unified Logic in setup/deploy.py
                 # It goes: 
                 # Tag exists remote? -> True. Release exists? -> Mocked False via check failure.
                 # "Tag X exists on remote... Force re-trigger CI?"
                 
                 mock_input.side_effect = ["0.2.0", "y"]
                 
                 # Mock check_call to handle 'gh release view' failure (Simulate check failure = release not found)
                 def side_effect_check_call(args, **kwargs):
                     if "gh release view" in " ".join(args):
                         raise subprocess.CalledProcessError(1, args)
                     return 0
                 mock_check_call.side_effect = side_effect_check_call
                 mock_call.return_value = 0

                 self.dm.deploy_release("0.1.0")
                 
                 # Verify delete call
                 mock_check_call.assert_any_call(["git", "push", "--delete", "origin", "v0.2.0"])
                 # Verify push call
                 mock_check_call.assert_any_call(["git", "push", "origin", "v0.2.0"])

if __name__ == '__main__':
    unittest.main()
