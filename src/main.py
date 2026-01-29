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
        from ui.app import StoryLordApp
        app = StoryLordApp()
        app.run()
