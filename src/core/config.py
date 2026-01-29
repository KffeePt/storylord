import os
from pathlib import Path

# System Globals
STORY_LORD_ROOT = os.path.expanduser("~/Documents/StoryLord")
APP_DATA_ROOT = os.path.expanduser("~/.storylord")

_ACTIVE_STORY_ROOT = None
# Schemas are now global in AppData or properly managed? 
# User said "Centralize registry...". Let's put registry/schemas in APP_DATA_ROOT/schemas
_SCHEMAS_DIR = os.path.join(APP_DATA_ROOT, "schemas")

CATEGORIES = ["Canon", "Characters", "Rules", "Lore", "Composition", "Episodes"]

def ensure_global_root():
    if not os.path.exists(STORY_LORD_ROOT):
        os.makedirs(STORY_LORD_ROOT)
    
    if not os.path.exists(APP_DATA_ROOT):
        os.makedirs(APP_DATA_ROOT)

    # Ensure global schemas dir exists
    if not os.path.exists(_SCHEMAS_DIR):
        os.makedirs(_SCHEMAS_DIR)

def set_story_root(story_name_or_path: str):
    """
    Sets the active story.
    If argument is an absolute path, use it.
    If it's a name, assume it's under STORY_LORD_ROOT/stories. 
    (Updated to use a 'stories' subdir to keep root clean, or just root?)
    Original was direct child of STORY_LORD_ROOT.
    """
    global _ACTIVE_STORY_ROOT
    
    ensure_global_root()
    
    if os.path.isabs(story_name_or_path):
        target = story_name_or_path
    else:
        # Check if "stories" subdir exists, if so use it, else root
        stories_dir = os.path.join(STORY_LORD_ROOT, "stories")
        if os.path.exists(stories_dir):
             target = os.path.join(stories_dir, story_name_or_path)
        else:
             target = os.path.join(STORY_LORD_ROOT, story_name_or_path)
    
    _ACTIVE_STORY_ROOT = os.path.abspath(target)
    
    # Ensure story structure exists
    if not os.path.exists(_ACTIVE_STORY_ROOT):
        try:
            os.makedirs(_ACTIVE_STORY_ROOT)
        except OSError:
            pass # Might be checking existence

def get_schemas_dir() -> str:
    # return Global Schemas Dir
    return _SCHEMAS_DIR

def is_story_set() -> bool:
    return _ACTIVE_STORY_ROOT is not None

def get_story_name() -> str:
    if _ACTIVE_STORY_ROOT:
        return os.path.basename(_ACTIVE_STORY_ROOT)
    return "Unknown"

# Versioning
from core.version_manager import VersionManager
_VERSION_MANAGER = VersionManager(os.path.join(APP_DATA_ROOT, "config", "config.json"))

def get_app_version() -> str:
    return _VERSION_MANAGER.get_version()

def get_version_manager() -> VersionManager:
    return _VERSION_MANAGER
