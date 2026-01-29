import os
import json
from prompt_toolkit.styles import Style
from core.config import APP_DATA_ROOT

DEFAULT_THEME = {
    # Base
    '': '#e0e0e0 bg:#1e1e1e', # Light text, Dark bg
    
    # Components
    'header': 'bg:#d4af37 #1e1e1e bold', # Gold bg, Dark text
    'sidebar': 'bg:#252526 #e0e0e0', # VS Code-ish sidebar
    'sidebar-active-blur': '#888888',
    
    # Menu
    'menu-selected': 'bg:#d4af37 #1e1e1e bold', # Gold highlight
    'menu-item': '#8fbcbb', # Pastel Teal
    'special-storyboard': 'bg:#d4af37 #000000 bold', # Gold bg, Black text (Special)
    
    # Status
    'error': '#ff5555 bg:#1e1e1e bold', # Pastel Red text
    'success': '#a3be8c bg:#1e1e1e bold', # Pastel Green text
    'warning': '#ebcb8b bg:#1e1e1e', # Pastel Yellow
    
    # Frames
    'gold-frame': 'bg:#1e1e1e #d4af37 border:#d4af37',
    'line': '#444444', # Dark grey separator
    'launcher-content': 'bg:#1e1e1e #e0e0e0',
}

class ThemeManager:
    def __init__(self):
        self.theme_path = os.path.join(APP_DATA_ROOT, "config", "theme.json")
        self.current_theme = DEFAULT_THEME.copy()
        self.load_theme()
        
    def load_theme(self):
        if os.path.exists(self.theme_path):
            try:
                with open(self.theme_path, "r") as f:
                    user_theme = json.load(f)
                    self.current_theme.update(user_theme)
            except Exception as e:
                print(f"Error loading theme: {e}")
        else:
            # Create default if not exists
            self.save_theme()
            
    def save_theme(self):
        try:
            config_dir = os.path.dirname(self.theme_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(self.theme_path, "w") as f:
                json.dump(self.current_theme, f, indent=4)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def get_style(self):
        return Style.from_dict(self.current_theme)

# Global Instance
theme_manager = ThemeManager()
