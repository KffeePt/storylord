import sys
import os

# Ensure we can import modules from directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from cli import main as cli_main
    
    # Attempt to handle as CLI command
    # If no args provided (or handled), returns False to proceed to TUI
    handled = False
    if len(sys.argv) > 1:
        handled = cli_main()
        

    if not handled:
        from core.instance_manager import ensure_single_instance
        ensure_single_instance()

        # Auto-Update Check (Only in Frozen/Compiled Mode)
        if getattr(sys, 'frozen', False):
            try:
                from core.updater import UpdateChecker
                from core.config import get_app_version
                from prompt_toolkit.shortcuts import yes_no_dialog, message_dialog
                import threading

                # Run check in main thread for now to keep it simple, 
                # or thread it? If we thread it, we can't block startup easily.
                # User wants "When it runs it will prompt". So blocking is fine/expected.
                # But we should show some "Checking..." status?
                # For now, simplistic sync check.
                
                print("Checking for updates...")
                checker = UpdateChecker()
                current_ver = get_app_version()
                has_update, latest_ver, release_data = checker.check_for_update(current_ver)
                
                if has_update:
                    should_update = yes_no_dialog(
                        title="Update Available",
                        text=f"A new version ({latest_ver}) is available (Current: {current_ver}).\n\nUnknown changes.\n\nUpdate now?"
                    ).run()
                    
                    if should_update:
                        is_portable = not checker.is_installed_mode()
                        print("Downloading update...")
                        path = checker.download_update(release_data, portable=is_portable)
                        
                        if path:
                            if is_portable:
                                message_dialog(
                                    title="Update Downloaded",
                                    text=f"Portable version downloaded to:\n{path}\n\nThe application will now close."
                                ).run()
                                checker.run_update(path)
                                sys.exit(0)
                            else:
                                # Installer
                                checker.run_update(path)
                                sys.exit(0)
            except Exception as e:
                # Don't crash app on update failure
                print(f"Auto-Update Failed: {e}")
        
        from ui.app import StoryLordApp
        app = StoryLordApp()
        app.run()

