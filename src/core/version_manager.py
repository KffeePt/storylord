
import json
import os
import subprocess
from typing import Optional

class VersionManager:
    """
    Manages the application version.
    Prioritizes Git tags (via `git describe`).
    Falls back to config.json if not in a git repo or no tags found.
    """
    
    DEFAULT_VERSION = "v0.0.1_alpha"

    def __init__(self, config_path: str):
        self.config_path = config_path
        self._version: str = self.DEFAULT_VERSION
        self._ensure_config_exists()
        self.load_version()

    def _ensure_config_exists(self):
        """Creates the config directory and file if they don't exist."""
        directory = os.path.dirname(self.config_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                pass 

        if not os.path.exists(self.config_path):
            self.save_version_to_config(self.DEFAULT_VERSION)

    def get_git_version(self) -> Optional[str]:
        """Tries to get version from git tags."""
        try:
            # git describe --tags --abbrev=0 gets the latest tag name
            version = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"], 
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            return version
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def load_version(self) -> str:
        """Loads version from Git, falling back to config file."""
        git_ver = self.get_git_version()
        if git_ver:
            self._version = git_ver
            # Auto-sync to config for persistence/backup
            self.save_version_to_config(git_ver)
            return self._version

        # Fallback to config
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._version = data.get("version", self.DEFAULT_VERSION)
        except (FileNotFoundError, json.JSONDecodeError):
            self._version = self.DEFAULT_VERSION
        return self._version

    def save_version_to_config(self, version: str):
        """Saves version to config file (backup/fallback)."""
        data = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass

        data["version"] = version
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except OSError:
            pass # benign failure

    def get_version(self) -> str:
        """Returns the current resolved version."""
        # Reload to ensure freshness if called multiple times or during deploy
        return self.load_version()

    def bump_minor(self, stage: str = "beta"):
        """
        Bumps Y in vX.Y.Z_stage. 
        NOTE: This now only updates the config/local state.
        To make it official, a git tag must be created.
        """
        major, minor, patch, _ = self._parse_version(self._version)
        new_ver = f"v{major}.{minor + 1}.0_{stage}"
        self._version = new_ver
        self.save_version_to_config(new_ver)
        return new_ver

    def bump_patch(self, stage: str = "alpha"):
        """Bumps Z in vX.Y.Z_stage"""
        major, minor, patch, _ = self._parse_version(self._version)
        new_ver = f"v{major}.{minor}.{patch + 1}_{stage}"
        self._version = new_ver
        self.save_version_to_config(new_ver)
        return new_ver

    def _parse_version(self, version_str: str) -> tuple[int, int, int, str]:
        try:
            # Strip 'v' if present
            clean_str = version_str.lstrip('v')
            
            # Split suffix if present
            stage = "alpha"
            if '_' in clean_str:
                parts = clean_str.split('_')
                clean_str = parts[0]
                if len(parts) > 1:
                    stage = parts[1]
            
            parts = clean_str.split('.')
            if len(parts) >= 3:
                return int(parts[0]), int(parts[1]), int(parts[2]), stage
            elif len(parts) == 2:
                return int(parts[0]), int(parts[1]), 0, stage
            elif len(parts) == 1:
                return int(parts[0]), 0, 0, stage
            return 0, 0, 1, stage
        except ValueError:
            return 0, 0, 1, "alpha"

if __name__ == "__main__":
    import argparse
    import sys
    
    config_path = os.path.join(os.path.expanduser("~/Documents/StoryLord/config/config.json"))
    vm = VersionManager(config_path)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--bump", choices=["feature", "fix"], help="Bump version based on type (Logic Only, DOES NOT TAG)")
    parser.add_argument("--set", help="Force set version string (overrides bump)")
    parser.add_argument("--stage", choices=["alpha", "beta", "prod"], default=None, help="Set stability stage")
    parser.add_argument("--get", action="store_true", help="Print current version")
    args = parser.parse_args()
    
    if args.set:
        vm.save_version_to_config(args.set)
        print(f"Version manually set to {vm.get_version()} (Config Only)")
    elif args.bump:
        stage = args.stage
        if args.bump == "feature":
            if not stage: stage = "beta"
            new_ver = vm.bump_minor(stage=stage)
            print(f"Bumped to {new_ver}. Run: git tag {new_ver}")
        else:
            if not stage: stage = "alpha"
            new_ver = vm.bump_patch(stage=stage)
            print(f"Bumped to {new_ver}. Run: git tag {new_ver}")
    elif args.get:
        print(vm.get_version())
    else:
        print(f"Current version (Git Prority): {vm.get_version()}")
