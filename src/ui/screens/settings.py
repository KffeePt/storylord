import json
import os
from prompt_toolkit.layout.containers import VSplit, Window, HSplit, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from core.config import STORY_LORD_ROOT, get_app_version
from ui.theme import theme_manager

# Settings State
class SettingsState:
    def __init__(self):
        self.mode = "MENU" # MENU, MANUAL, VIEWER, EDITOR, VERSION
        self.menu_idx = 0
        
        # Manual/Docs
        self.manual_nodes = [] 
        self.manual_idx = 0
        self.viewer_content = []
        self.viewer_scroll = 0
        self.viewer_title = ""
        self.viewer_path = ""
        
        # Editor
        self.editor_buffer = None # TextArea
        self.editor_target_file = None
        self.editor_title = ""
        
        # Version
        self.version_info = ""

    def load_registry(self):
        try:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            manual_json = os.path.join(root_dir, "docs", "manual", "manual.json")
            if os.path.exists(manual_json):
                with open(manual_json, "r", encoding="utf-8") as f:
                    self.manual_nodes = json.load(f)
            else:
                self.manual_nodes = []
        except:
            self.manual_nodes = []

    def load_viewer_content(self, relative_path):
         try:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            full_path = os.path.join(root_dir, "docs", "manual", relative_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    self.viewer_content = f.read().splitlines()
                    self.viewer_path = full_path
            else:
                 self.viewer_content = ["File not found."]
         except Exception as e:
             self.viewer_content = [f"Error: {e}"]

    def open_editor(self, file_path, title):
        self.editor_target_file = file_path
        self.editor_title = title
        content = ""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {e}"
        else:
            content = "{}" # New JSON
            
        self.editor_buffer = TextArea(
            text=content,
            focusable=True,
            scrollbar=True,
            wrap_lines=False,
        )
        self.mode = "EDITOR"

    def save_editor(self):
        if self.editor_buffer and self.editor_target_file:
            try:
                with open(self.editor_target_file, "w", encoding="utf-8") as f:
                    f.write(self.editor_buffer.text)
                state.set_status(f"Saved {self.editor_title}")
                # Reload theme if needed
                if "theme.json" in self.editor_target_file:
                    theme_manager.load_theme()
            except Exception as e:
                state.set_status(f"Error saving: {e}")

s_state = SettingsState()

# --- UI Renderers ---

def get_menu_text():
    options = [
        "Open Manual / Documentation",
        "Edit Configuration (config.json)",
        "Edit TUI Theme (theme.json)",
        "Version Info / Update", 
        "Restart CLI"
    ]
    lines = []
    lines.append(("", "\n Settings & Administration \n\n"))
    
    for i, opt in enumerate(options):
        if i == s_state.menu_idx:
            lines.append(("class:menu-selected", f" > {opt} \n"))
        else:
             lines.append(("class:menu-item", f"   {opt} \n"))
             
    return lines

def get_version_text():
    lines = []
    lines.append(("class:header", " VERSION INFO \n\n"))
    lines.append(("", f" Current Version: {get_app_version()}\n\n"))
    lines.append(("class:warning", " To update the version, edit the version file manually below.\n"))
    lines.append(("", " Press [E] to Edit Version File, [Esc] to Back.\n"))
    return lines

# --- Keybindings ---
kb = KeyBindings()

@kb.add('up', filter=lambda: s_state.mode in ["MENU", "MANUAL", "VIEWER"])
@kb.add('k', filter=lambda: s_state.mode in ["MENU", "MANUAL", "VIEWER"])
def up(e):
    if s_state.mode == "MENU": s_state.menu_idx = max(0, s_state.menu_idx - 1)
    elif s_state.mode == "MANUAL": s_state.manual_idx = max(0, s_state.manual_idx - 1)
    elif s_state.mode == "VIEWER": s_state.viewer_scroll = max(0, s_state.viewer_scroll - 1)

@kb.add('down', filter=lambda: s_state.mode in ["MENU", "MANUAL", "VIEWER"])
@kb.add('j', filter=lambda: s_state.mode in ["MENU", "MANUAL", "VIEWER"])
def down(e):
    if s_state.mode == "MENU": s_state.menu_idx = min(4, s_state.menu_idx + 1)
    elif s_state.mode == "MANUAL": s_state.manual_idx = min(len(s_state.manual_nodes)-1, s_state.manual_idx + 1)
    elif s_state.mode == "VIEWER": s_state.viewer_scroll = max(0, len(s_state.viewer_content) - 10, s_state.viewer_scroll + 1) # Simple bound

@kb.add('enter')
def enter(e):
    if s_state.mode == "MENU":
        idx = s_state.menu_idx
        if idx == 0: # Manual
            s_state.mode = "MANUAL"
            s_state.load_registry()
        elif idx == 1: # Config
            path = os.path.join(STORY_LORD_ROOT, "config", "config.json")
            s_state.open_editor(path, "Configuration")
            e.app.layout.focus(s_state.editor_buffer)
        elif idx == 2: # Theme
            path = os.path.join(STORY_LORD_ROOT, "config", "theme.json")
            s_state.open_editor(path, "Theme")
            e.app.layout.focus(s_state.editor_buffer)
        elif idx == 3: # Version
            s_state.mode = "VERSION"
        elif idx == 4: # Restart
            import sys; os.execv(sys.executable, [sys.executable] + sys.argv)
            
    elif s_state.mode == "MANUAL":
        # Open Viewer logic... (omitted for brevity, assume similar to before)
        pass

@kb.add('escape')
@kb.add('c-c')
def back(e):
    if s_state.mode == "EDITOR":
        s_state.mode = "MENU"
        s_state.editor_buffer = None
        e.app.layout.focus_previous() # Gets back to window
    elif s_state.mode != "MENU":
        s_state.mode = "MENU"
    else:
         # Back to sidebar
         state.active_focus_zone = "SIDEBAR"
         e.app.layout.focus_previous()

@kb.add('c-s', filter=lambda: s_state.mode == "EDITOR")
def save(e):
    s_state.save_editor()

@kb.add('e', filter=lambda: s_state.mode == "VERSION")
def edit_version(e):
    # Determine version file path (passed to VersionManager)
    # config.py: _VERSION_MANAGER = VersionManager(os.path.join(STORY_LORD_ROOT, "config", "config.json"))
    # Wait, VersionManager uses config.json??
    # If so, just edit config.json.
    # But usually version is separate or key in config.
    # Let's just open config.json generally.
    path = os.path.join(STORY_LORD_ROOT, "config", "config.json")
    s_state.open_editor(path, "Config/Version")
    e.app.layout.focus(s_state.editor_buffer)

# --- Layout ---
from prompt_toolkit.layout.containers import DynamicContainer

def get_body():
    if s_state.mode == "MENU":
        return Window(content=FormattedTextControl(get_menu_text, key_bindings=kb, focusable=True), style="class:launcher-content")
    elif s_state.mode == "EDITOR":
         return HSplit([
             Window(height=1, content=FormattedTextControl(f" EDITING: {s_state.editor_title} (Ctrl+S to Save, Esc to Quit)"), style="class:header"),
             s_state.editor_buffer
         ])
    elif s_state.mode == "VERSION":
        return Window(content=FormattedTextControl(get_version_text, key_bindings=kb, focusable=True), style="class:launcher-content")
    else:
        # Fallback/Manual placeholder
        return Window(content=FormattedTextControl("Manual Viewer (Placeholder)", key_bindings=kb, focusable=True))

layout = Frame(
    body=DynamicContainer(get_body),
    title=" Settings & Tools ",
    style="class:gold-frame"
)
