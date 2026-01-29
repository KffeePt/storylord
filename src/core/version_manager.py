
import json
import os
from typing import Optional

class VersionManager:
    """
    Manages the application version stored in the config.json file.
    Follows Semantic Versioningish rules:
    - Feature (feat) -> 0.1 bump
    - Fix/Other (fix, build, etc) -> 0.0.1 bump
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
                pass # Handle permissions issues gracefully-ish

        if not os.path.exists(self.config_path):
            self.save_version(self.DEFAULT_VERSION)

    def load_version(self) -> str:
        """Loads version from config file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._version = data.get("version", self.DEFAULT_VERSION)
        except (FileNotFoundError, json.JSONDecodeError):
            self._version = self.DEFAULT_VERSION
        return self._version

    def save_version(self, version: str):
        """Saves version to config file."""
        self._version = version
        data = {}
        
        # Read existing data to preserve other keys
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass

        data["version"] = version
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_version(self) -> str:
        return self._version

    def bump_minor(self, stage: str = "beta"):
        """Bumps Y in vX.Y.Z_stage"""
        major, minor, patch, _ = self._parse_version(self._version)
        self.save_version(f"v{major}.{minor + 1}.0_{stage}")

    def bump_patch(self, stage: str = "alpha"):
        """Bumps Z in vX.Y.Z_stage"""
        major, minor, patch, _ = self._parse_version(self._version)
        self.save_version(f"v{major}.{minor}.{patch + 1}_{stage}")

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
    
    # Path might be relative if running from root
    # Default assumption: running from repo root
    # Adjust path to find config relative to this script or CWD? 
    # Use standard location for now
    config_path = os.path.join(os.path.expanduser("~/Documents/StoryLord/config/config.json"))
    
    vm = VersionManager(config_path)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--bump", choices=["feature", "fix"], help="Bump version based on type")
    parser.add_argument("--set", help="Force set version string (overrides bump)")
    parser.add_argument("--stage", choices=["alpha", "beta", "prod"], default=None, help="Set stability stage")
    parser.add_argument("--get", action="store_true", help="Print current version")
    args = parser.parse_args()
    
    if args.set:
        vm.save_version(args.set)
        print(f"Version manually set to {vm.get_version()}")
    elif args.bump:
        stage = args.stage
        if args.bump == "feature":
            # Feature default -> beta if not specified
            if not stage: stage = "beta"
            vm.bump_minor(stage=stage)
            print(f"Bumped to {vm.get_version()} (Feature)")
        else:
            # Fix default -> alpha if not specified
            if not stage: stage = "alpha"
            vm.bump_patch(stage=stage)
            print(f"Bumped to {vm.get_version()} (Fix)")
    elif args.get:
        print(vm.get_version())
    else:
        print(f"Current version: {vm.get_version()}")
