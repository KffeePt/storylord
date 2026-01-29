from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.layout import Layout
from prompt_toolkit.filters import Condition

from ui.layout import create_layout, SCREENS
from ui.state import state

# Import Screens to register them
from ui.screens import dashboard, generator, explorer, sync, launcher, storyboard, settings
from core.config import get_app_version

def register_screens():
    SCREENS["LAUNCHER"] = launcher.layout
    SCREENS["DASHBOARD"] = dashboard.layout
    SCREENS["GENERATOR"] = generator.layout
    SCREENS["EXPLORER"] = explorer.layout
    SCREENS["SYNC"] = sync.layout
    SCREENS["STORYBOARD"] = storyboard.layout
    SCREENS["SETTINGS"] = settings.layout

class StoryLordApp:
    def __init__(self):
        register_screens()
        
        self.layout = Layout(create_layout())
        self.kb = KeyBindings()
        self.setup_global_bindings()
        
        from ui.theme import theme_manager
        self.style = theme_manager.get_style()
        
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
            mouse_support=True,
        )
    
    
    def setup_global_bindings(self):
        @self.kb.add('c-c')
        @self.kb.add('q')
        def exit_(event):
             # Force clean exit
             import sys
             sys.exit(0)
            
        # Global shortcuts for power users, but Menu System is primary.

        
        
        @self.kb.add('escape', 'r')
        def restart_app(event):
             # ALT+R
             import os
             import sys
             os.execv(sys.executable, [sys.executable] + sys.argv)
             
        @self.kb.add('escape', 'd')
        def toggle_debug(event):
            # ALT+D
            state.show_debug = not state.show_debug
            state.set_status(f"Debug: {state.show_debug}")
            

            
            state.set_status(f"Debug: {state.show_debug}")
            


        @self.kb.add('w')
        def debug_w(event):
             state.set_status("DEBUG: GLOBAL W CAUGHT (NO FOCUS TARGET?)")



    def run(self):
        self.app.run()
