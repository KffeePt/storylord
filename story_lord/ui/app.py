from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.layout import Layout
from prompt_toolkit.filters import Condition

from ui.layout import create_layout, SCREENS
from ui.state import state

# Import Screens to register them
from ui.screens import dashboard, generator, explorer, sync, launcher

def register_screens():
    SCREENS["LAUNCHER"] = launcher.layout
    SCREENS["DASHBOARD"] = dashboard.layout
    SCREENS["GENERATOR"] = generator.layout
    SCREENS["EXPLORER"] = explorer.layout
    SCREENS["SYNC"] = sync.layout

class StoryLordApp:
    def __init__(self):
        register_screens()
        
        self.layout = Layout(create_layout())
        self.kb = KeyBindings()
        self.setup_global_bindings()
        
        self.style = Style.from_dict({
            # Base
            '': '#e0e0e0 bg:#1e1e1e', # Light text, Dark bg
            
            # Components
            'header': 'bg:#d4af37 #1e1e1e bold', # Gold bg, Dark text
            'sidebar': 'bg:#252526 #e0e0e0', # VS Code-ish sidebar
            
            # Menu
            'menu-selected': 'bg:#d4af37 #1e1e1e bold', # Gold highlight
            'menu-item': '#8fbcbb', # Pastel Teal
            
            # Status
            'error': '#ff5555 bg:#1e1e1e bold', # Pastel Red text
            'success': '#a3be8c bg:#1e1e1e bold', # Pastel Green text
            'warning': '#ebcb8b bg:#1e1e1e', # Pastel Yellow
            
            # Frames
            'gold-frame': 'bg:#1e1e1e #d4af37 border:#d4af37',
            'launcher-content': 'bg:#1e1e1e #e0e0e0',
        })
        
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
            mouse_support=True
        )
    
    
    def setup_global_bindings(self):
        @self.kb.add('c-c')
        def exit_(event):
             # Force clean exit
             import sys
             sys.exit(0)
            
        # Global shortcuts for power users, but Menu System is primary.
        @self.kb.add('f1')
        def dash(event): 
            state.active_screen = "DASHBOARD"
            event.app.layout.focus(dashboard.layout)
        # ... (others remain)
        
        @self.kb.add('f2')
        def gen(event): 
            state.active_screen = "GENERATOR"
            event.app.layout.focus(generator.layout)
        
        @self.kb.add('f3')
        def exp(event): 
            state.active_screen = "EXPLORER"
            from ui.screens import explorer
            explorer.refresh() 
            event.app.layout.focus(explorer.layout)
            
        @self.kb.add('f4')
        def sync(event): 
            state.active_screen = "SYNC"
            from ui.screens import sync
            sync.refresh()
            event.app.layout.focus(sync.layout)

    def run(self):
        self.app.run()
