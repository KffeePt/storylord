import os
from pathlib import Path

# System Globals
STORY_LORD_ROOT = os.path.expanduser("~/Documents/StoryLord")
_ACTIVE_STORY_ROOT = None
_SCHEMAS_DIR = None

CATEGORIES = ["Canon", "Characters", "Rules", "Lore", "Composition", "Episodes"]

def ensure_global_root():
    if not os.path.exists(STORY_LORD_ROOT):
        os.makedirs(STORY_LORD_ROOT)

def set_story_root(story_name_or_path: str):
    """
    Sets the active story.
    If argument is an absolute path, use it.
    If it's a name, assume it's under STORY_LORD_ROOT.
    """
    global _ACTIVE_STORY_ROOT, _SCHEMAS_DIR
    
    ensure_global_root()
    
    if os.path.isabs(story_name_or_path):
        target = story_name_or_path
    else:
        target = os.path.join(STORY_LORD_ROOT, story_name_or_path)
    
    _ACTIVE_STORY_ROOT = os.path.abspath(target)
    _SCHEMAS_DIR = os.path.join(_ACTIVE_STORY_ROOT, "schemas")
    
    # Ensure story structure exists
    if not os.path.exists(_SCHEMAS_DIR):
        os.makedirs(_SCHEMAS_DIR)

def get_schemas_dir() -> str:
    if _SCHEMAS_DIR is None:
        raise RuntimeError("Story Root not set. Please select a story first.")
    return _SCHEMAS_DIR

def is_story_set() -> bool:
    return _ACTIVE_STORY_ROOT is not None

def get_story_name() -> str:
    if _ACTIVE_STORY_ROOT:
        return os.path.basename(_ACTIVE_STORY_ROOT)
    return "Unknown"

# Versioning
from core.version_manager import VersionManager
_VERSION_MANAGER = VersionManager(os.path.join(STORY_LORD_ROOT, "config", "config.json"))

def get_app_version() -> str:
    return _VERSION_MANAGER.get_version()

def get_version_manager() -> VersionManager:
    return _VERSION_MANAGER
