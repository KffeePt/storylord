import os
import json
import re
from typing import Dict
from .config import get_specs_dir
from .models import StoryMetadata, StorySpec

def get_metadata_file():
    return os.path.join(get_specs_dir(), "_metadata.json")

def load_all_metadata() -> StoryMetadata:
    meta_file = get_metadata_file()
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return StoryMetadata(**raw_data)
        except Exception as e:
            # If load fails, return empty
            print(f"Warning: Failed to load metadata: {e}")
            return StoryMetadata()
    return StoryMetadata()

def save_all_metadata(data: StoryMetadata) -> None:
    """
    Saves the full StoryMetadata object to _metadata.json.
    """
    with open(get_metadata_file(), "w", encoding="utf-8") as f:
        # Use mode='json' (pydantic v2) or .dict() (v1)
        # Using model_dump for v2 compatibility layer if needed, assuming v2
        try:
            json.dump(data.model_dump(), f, indent=4, sort_keys=True)
        except AttributeError:
             # Fallback for Pydantic v1 if installed
            json.dump(data.dict(), f, indent=4, sort_keys=True)

def parse_header_from_file(filepath: str) -> StorySpec:
    """
    Reads the first 20 lines of a file to extract YAML-like headers.
    Returns a StorySpec object with defaults for missing fields.
    """
    meta = {}
    # Defaults
    meta["title"] = os.path.basename(filepath).replace(".md","").replace("_", " ")
    meta["category"] = "Unknown"
    meta["version"] = "0.1"
    meta["description"] = ""
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            head = lines[:20]
        content = "".join(head)
        for key in ["Title", "Description", "Category", "Version"]:
            match = re.search(fr"^{key}:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)
            if match:
                meta[key.lower()] = match.group(1).strip()
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        
    return StorySpec(**meta)

def update_file_header(filepath, new_meta):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        body_start_idx = 0
        for i, line in enumerate(lines):
            if not line.strip(): 
                body_start_idx = i + 1
                break
            if ":" not in line: 
                body_start_idx = i
                break
        
        body = lines[body_start_idx:]
        header_lines = []
        for key in ["Title", "Description", "Category", "Version"]:
             val = new_meta.get(key.lower(), "")
             header_lines.append(f"{key}: {val}\n")
        header_lines.append("\n") 
        
        new_content = "".join(header_lines) + "".join(body)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Failed to update file {filepath}: {e}")
        return False

def scan_and_sync():
    specs_dir = get_specs_dir()
    data = load_all_metadata() # StoryMetadata object
    
    on_disk_paths = set()
    
    for root, dirs, files in os.walk(specs_dir):
        if root == specs_dir: continue
        category = os.path.basename(root)
        for file in files:
            if not file.endswith(".md"): continue
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, specs_dir).replace("\\", "/")
            on_disk_paths.add(rel_path)
            
            # This returns a StorySpec object with defaults filled
            file_spec = parse_header_from_file(filepath)
            
            # Override category based on folder, just in case file header is wrong/missing
            # We trust the folder structure for category
            file_spec.category = category
            
            # Check if we need to write back (Auto-Heal) - Naive check: if header was empty, we filled defaults
            # A better way is to check the RAW headers again, but let's assume if we are creating a fresh Spec,
            # we should update the file if the existing file lacks headers.
            # For efficiency, update_file_header checks if content changes.
            update_file_header(filepath, file_spec.model_dump())
            
            data.specs[rel_path] = file_spec

    # Clean missing
    existing_keys = list(data.specs.keys())
    for key in existing_keys:
        if key not in on_disk_paths:
            del data.specs[key]
            
    save_all_metadata(data)
    return data
