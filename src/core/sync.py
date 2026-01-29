import os
from .metadata import load_all_metadata, parse_header_from_file, scan_and_sync
from .config import get_schemas_dir, is_story_set

def check_sync_status():
    specs_dir = get_schemas_dir()
    issues = []
    data = load_all_metadata() # StoryMetadata
    specs = data.specs # Access Model field
    
    disk_files = set()
    for root, dirs, files in os.walk(specs_dir):
        if root == specs_dir: continue
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, specs_dir).replace("\\", "/")
                disk_files.add(rel_path)
                
                if rel_path not in specs:
                    issues.append({"file": rel_path, "status": "MISSING_IN_JSON", "details": "Not in metadata DB."})
                else:
                    file_meta = parse_header_from_file(full_path)
                    json_meta = specs[rel_path]
                    mismatches = []
                    for k in ["title", "version", "category"]:
                        if getattr(file_meta, k, "") != getattr(json_meta, k, ""):
                            mismatches.append(f"{k} mismatch")
                    if mismatches:
                        issues.append({"file": rel_path, "status": "METADATA_MISMATCH", "details": ", ".join(mismatches)})

    for rel_path in specs:
        if rel_path not in disk_files:
            issues.append({"file": rel_path, "status": "MISSING_ON_DISK", "details": "File missing."})
            
    return issues

def fix_all_issues():
    # Calling scan_and_sync handles "missing in json" and "updates matching files to disk"
    # It basically heals the state.
    # What about "missing on disk"? scan_and_sync cleans that too.
    scan_and_sync()
    return "Rescanned and synchronized."
