import argparse
import sys
import os
import json
from core.config import set_story_root, get_specs_dir, STORY_LORD_ROOT, ensure_global_root, CATEGORIES
from core.models import StoryMetadata, StorySpec
from core.metadata import load_all_metadata, parse_header_from_file, save_all_metadata
from core.generator import generate_spec

def main():
    parser = argparse.ArgumentParser(description="Story Lord v3 CLI", formatter_class=argparse.RawTextHelpFormatter)
    
    # Global Flags
    parser.add_argument("--story", help="Explicitly set the story name or path.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    
    subparsers = parser.add_subparsers(dest="noun", help="The object to manipulate.")
    
    # --- STORY COMMANDS ---
    story_parser = subparsers.add_parser("story", help="Manage story projects.")
    story_subs = story_parser.add_subparsers(dest="verb", help="Action to perform.")
    
    # story list
    story_subs.add_parser("list", help="List all available stories.")
    
    # story create
    create_story = story_subs.add_parser("create", help="Create a new story.")
    create_story.add_argument("name", help="Name of the new story.")
    
    # --- SPEC COMMANDS ---
    spec_parser = subparsers.add_parser("spec", help="Manage story specifications.")
    spec_subs = spec_parser.add_subparsers(dest="verb", help="Action to perform.")
    
    # spec list
    spec_subs.add_parser("list", help="List specs in the current story.")
    
    # spec create
    create_spec = spec_subs.add_parser("create", help="Create a new spec file.")
    create_spec.add_argument("category", help=f"Category: {', '.join(CATEGORIES)}")
    create_spec.add_argument("title", help="Title of the spec.")
    create_spec.add_argument("--desc", default="", help="Description.")
    
    # spec read
    read_spec = spec_subs.add_parser("read", help="Read a spec content.")
    read_spec.add_argument("path", help="Relative path to spec (e.g. Lore/MySpec.md).")
    
    # --- TREE COMMAND ---
    subparsers.add_parser("tree", help="Visual tree content of specs.")
    
    # --- ANALYZE COMMAND ---
    subparsers.add_parser("analyze", help="Show statistics.")

    args = parser.parse_args()
    
    if not args.noun:
        return False # Fallback to TUI
        
    # --- EXECUTION ---
    
    # 1. Setup Story Context
    ensure_global_root()
    active_story = None
    if args.story:
        set_story_root(args.story)
        active_story = args.story
    else:
        # Try cwd or default? CLI usually requires explicit context or CWD.
        # Let's assume CWD is a story if specs folder exists
        if os.path.exists("specs"):
            set_story_root(os.getcwd())
            active_story = os.getcwd()
        else:
            # If command is 'story list' or 'story create', we don't need a context
            if not (args.noun == "story" and args.verb in ["list", "create"]):
                 if args.json:
                     print(json.dumps({"error": "No story context. Use --story or run in story folder."}))
                 else:
                     print("Error: No story context. Use --story <name> or run command from a story directory.")
                 sys.exit(1)

    # 2. Handler
    output = {}
    
    if args.noun == "story":
        if args.verb == "list":
            stories = [f for f in os.listdir(STORY_LORD_ROOT) if os.path.isdir(os.path.join(STORY_LORD_ROOT, f))]
            if args.json:
                print(json.dumps(stories))
            else:
                print(f"Stories in {STORY_LORD_ROOT}:")
                for s in stories: print(f" - {s}")
                
        elif args.verb == "create":
            path = os.path.join(STORY_LORD_ROOT, args.name)
            if os.path.exists(path):
                print(f"Error: {args.name} already exists.")
            else:
                os.makedirs(os.path.join(path, "specs"))
                print(f"Created story: {path}")
                
    elif args.noun == "spec":
        if args.verb == "list":
            data = load_all_metadata()
            if args.json:
                print(json.dumps([s.model_dump() for s in data.specs.values()]))
            else:
                for path, spec in data.specs.items():
                    print(f"[{spec.category}] {spec.title} ({path})")
                    
        elif args.verb == "create":
            if args.category not in CATEGORIES:
                print(f"Invalid category. Options: {CATEGORIES}")
                sys.exit(1)
            
            success, msg = generate_spec(args.category, args.title, description=args.desc)
            if args.json:
                print(json.dumps({"success": success, "message": msg}))
            else:
                print(msg)
                
        elif args.verb == "read":
            full_path = os.path.join(get_specs_dir(), args.path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if args.json:
                    print(json.dumps({"path": args.path, "content": content}))
                else:
                    print(content)
            else:
                print("File not found.")
                
    elif args.noun == "tree":
        # Simple tree
        root = get_specs_dir()
        if args.json:
             # Recursive dict
             def dirtree(p):
                 return {d.name: dirtree(d) for d in os.scandir(p) if d.is_dir()} | {f.name: None for f in os.scandir(p) if f.is_file()}
             print(json.dumps(dirtree(root)))
        else:
            for root, dirs, files in os.walk(root):
                level = root.replace(get_specs_dir(), '').count(os.sep)
                indent = ' ' * 4 * (level)
                print(f'{indent}{os.path.basename(root)}/')
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    print(f'{subindent}{f}')
                    
    elif args.noun == "analyze":
        data = load_all_metadata()
        stats = {
            "total_specs": len(data.specs),
            "categories": {}
        }
        for s in data.specs.values():
            stats["categories"][s.category] = stats["categories"].get(s.category, 0) + 1
            
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("Analysis:")
            print(f" Total Specs: {stats['total_specs']}")
            print(" Categories:")
            for k, v in stats["categories"].items():
                print(f"  - {k}: {v}")

    return True # CLI handled execution
