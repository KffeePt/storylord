import os
import re
from .metadata import update_file_header
from .config import get_specs_dir
from .models import StorySpec

TEMPLATES_BODY = {
    "Lore": "\n## Summary\n(One line explanation)\n\n## Mechanics\n(Rules)\n",
    "Characters": "\n## Role\n...\n\n## Background\n...\n",
    "Canon": "\n## Arc Description\n...\n\n## Key Events\n1. ...\n",
    "Rules": "\n## Rule Definition\n...\n\n## Exceptions\n...\n",
    "Composition": "\n## Visual Style\n...\n\n## Audio\n...\n",
    "Episodes": "\n## Logline\n...\n\n## Acts\n...\n"
}

def sanitize_filename(title):
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    return clean.replace(' ', '_').lower()

from typing import Tuple

def generate_spec(category: str, title: str, version: str = "0.1", description: str = "") -> Tuple[bool, str]:
    """
    Generates a new specification file from a template.
    
    Args:
        category: The category of the spec (e.g. Lore, Canon).
        title: The display title of the spec.
        version: Semantic version string.
        description: Brief description.
        
    Returns:
        (success, message) tuple.
    """
    # Validate via Model
    try:
        spec = StorySpec(title=title, category=category, version=version, description=description)
    except Exception as e:
        return False, f"Validation Error: {e}"

    specs_dir = get_specs_dir()
    cat_dir = os.path.join(specs_dir, category)
    if not os.path.exists(cat_dir):
        os.makedirs(cat_dir)
        
    filename = f"{sanitize_filename(title)}.md"
    filepath = os.path.join(cat_dir, filename)
    
    if os.path.exists(filepath):
        return False, f"File '{filename}' already exists."
        
    with open(filepath, "w", encoding="utf-8") as f:
        body = TEMPLATES_BODY.get(category, "\n# Content\n")
        f.write(body)
        
    meta = {
        "title": title,
        "category": category,
        "version": version,
        "description": description
    }
    update_file_header(filepath, meta)
    
    return True, filepath
