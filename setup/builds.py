import os
import sys
import subprocess
import shutil
import hashlib
import json
from .utils import Colors, DIST_DIR, countdown_or_wait, set_cursor_visible, validate_version_basic, prompt_version_stage, get_full_version

class BuildManager:
    def __init__(self):
        pass

    def get_file_hash(self, path):
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_manifest(self):
        print("Generating Manifest...")
        manifest = {}
        base_len = len(DIST_DIR) + 1
        
        if os.path.exists(DIST_DIR):
            for root, dirs, files in os.walk(DIST_DIR):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = full_path[base_len:] 
                    try:
                        h = self.get_file_hash(full_path)
                        manifest[rel_path] = h
                    except Exception as e:
                        print(f"Error hashing {rel_path}: {e}")
                    
            manifest_path = os.path.join(DIST_DIR, "manifest.json")
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"Manifest saved to {manifest_path}")

    def prepare_build_version(self):
        print(f"\n{Colors.CYAN}--- Build Version Configuration ---{Colors.ENDC}")
        print(f"Format: x.y.z (Example: {Colors.GREEN}0.2.1{Colors.ENDC})")
        
        # dynamic import to avoid circular dep if any (though unlikely here)
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
        from core.config import get_app_version
        current_ver = get_app_version()
        
        # Strip v and labels for the numerical prompt
        current_base = current_ver.lstrip('v').split('_')[0]
        
        while True:
            set_cursor_visible(True)
            tag_input = input(f"Enter Build Version [v{current_base}] (e.g. 0.5.0): ").strip()
            set_cursor_visible(False)
            
            if not tag_input:
                base_version = current_base
                break
            
            # Clean 'v' from input if user typed it
            base_version = tag_input.lstrip('v')
            
            if validate_version_basic(base_version):
                break
            else:
                print(f"{Colors.FAIL}Invalid format! Please use numbers and periods (e.g., 0.1.2){Colors.ENDC}")

        # Get stage
        current_parts = current_ver.split('_', 1)
        current_stage = f"_{current_parts[1]}" if len(current_parts) > 1 else ""
        
        stage = prompt_version_stage(current_stage)
        new_version = get_full_version(base_version, stage)


        
        # Always update version file if changed OR if user just confirmed current (to be safe? No, only if changed)
        if new_version != current_ver:
             print(f"Updating version to {new_version}...")
             try:
                version_file = os.path.join("src", "core", "_version.py")
                with open(version_file, "w") as f:
                    f.write(f'__version__ = "{new_version}"\n')
                print(f"{Colors.GREEN}Updated {version_file}{Colors.ENDC}")
             except Exception as e:
                print(f"{Colors.FAIL}Failed to update version file: {e}{Colors.ENDC}")
                return
        
        # Tag locally
        print(f"Creating local tag {new_version}...")
        try:
             # Check for uncommitted changes
             status = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
             if status:
                  set_cursor_visible(True)
                  do_commit = input("Uncommitted changes detected. Commit for tag? (Y/n): ").strip().lower() != 'n'
                  set_cursor_visible(False)
                  if do_commit:
                       subprocess.check_call(["git", "add", "."])
                       set_cursor_visible(True)
                       msg = input(f"Commit Message [chore: Build Version {new_version}]: ").strip() or f"chore: Build Version {new_version}"
                       set_cursor_visible(False)
                       subprocess.check_call(["git", "commit", "-m", msg])
             
             # Create tag
             # Check if tag exists
             tags = subprocess.check_output(["git", "tag"], stderr=subprocess.DEVNULL).decode("utf-8").splitlines()
             if new_version in tags:
                 set_cursor_visible(True)
                 overwrite = input(f"Tag {new_version} exists locally. Overwrite? (y/N): ").strip().lower() == 'y'
                 set_cursor_visible(False)
                 if overwrite:
                     subprocess.check_call(["git", "tag", "-f", new_version])
                     print(f"{Colors.GREEN}Tag updated locally.{Colors.ENDC}")
             else:
                 subprocess.check_call(["git", "tag", new_version])
                 print(f"{Colors.GREEN}Tagged {new_version} locally.{Colors.ENDC}")
                 
        except Exception as e:
             print(f"{Colors.WARNING}Tagging failed: {e}{Colors.ENDC}")


    def run_pyinstaller(self):
        print(f"{Colors.CYAN}Building Directory Executable with PyInstaller...{Colors.ENDC}")
        success = False
        try:
            dist_path = os.path.abspath("bin/Dist")
            work_path = os.path.abspath("bin/Build/Dir")
            
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                "--distpath", dist_path,
                "--workpath", work_path,
                "story_lord.spec"
            ])
            self.generate_manifest()
            print(f"{Colors.GREEN}Build Complete! Check {DIST_DIR}.{Colors.ENDC}")
            success = True
        except Exception as e:
            print(f"{Colors.FAIL}Build Failed: {e}{Colors.ENDC}")
            success = False
        
        countdown_or_wait(success)

    def run_pyinstaller_onefile(self):
        print(f"{Colors.CYAN}Building Single-File Executable...{Colors.ENDC}")
        success = False
        try:
            dist_path = os.path.abspath("bin/Portable")
            work_path = os.path.abspath("bin/Build/OneFile")
            
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                "--distpath", dist_path,
                "--workpath", work_path,
                "story_lord_onefile.spec"
            ])
            
            src = os.path.join(dist_path, "StoryLord.exe")
            dst = os.path.join(dist_path, "StoryLord-Portable.exe")
            if os.path.exists(src):
                if os.path.exists(dst): os.remove(dst)
                os.rename(src, dst)
                print(f"Renamed to {dst}")
                
            print(f"{Colors.GREEN}OneFile Build Complete! Check {dist_path}.{Colors.ENDC}")
            success = True
        except Exception as e:
            print(f"{Colors.FAIL}OneFile Build Failed: {e}{Colors.ENDC}")
            success = False
        
        countdown_or_wait(success)

    def _find_iscc(self):
        if shutil.which("iscc"):
            return "iscc"
        prog_files = [os.environ.get("ProgramFiles", "C:\\Program Files"), os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]
        for pf in prog_files:
            if not pf: continue
            for v in ["Inno Setup 6", "Inno Setup 5", "Inno Setup"]:
                candidate = os.path.join(pf, v, "ISCC.exe")
                if os.path.exists(candidate):
                    return candidate
        return None

    def run_inno_setup(self):
        print(f"{Colors.CYAN}Building Installer with Inno Setup...{Colors.ENDC}")
        success = False
        try:
            if not os.path.exists(os.path.join(DIST_DIR, "manifest.json")):
                 print(f"{Colors.WARNING}Warning: manifest.json not found in dist.{Colors.ENDC}")
            
            iscc_cmd = self._find_iscc()
            if not iscc_cmd:
                 raise FileNotFoundError("ISCC.exe not found.")
            
            # get version from core (hacky path access or ensure path in sys.path)
            # Assuming main entry point ensures src in path, we can import here
            from core.config import get_app_version
            version = get_app_version()
            if not version.startswith("v"):
                version = f"v{version}"
            
            output_name = f"StoryLordSetup_{version}"
            print(f"Building Installer: {output_name}")

            subprocess.check_call([
                iscc_cmd, 
                f"/DMyAppVersion={version}", 
                f"/DOutputFileName={output_name}",
                f'/DSourceDir={DIST_DIR}', 
                "installer.iss"
            ])
            print(f"{Colors.GREEN}Installer Complete! Check bin/Installer.{Colors.ENDC}")
            success = True
        except Exception as e:
            print(f"{Colors.FAIL}Installer Build Failed: {e}{Colors.ENDC}")
            success = False
        
        countdown_or_wait(success)
