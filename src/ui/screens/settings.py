import json
from prompt_toolkit.layout.containers import VSplit, Window, HSplit, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
import os

# Settings State
class SettingsState:
    def __init__(self):
        self.mode = "MENU" # MENU, MANUAL, VIEWER
        self.menu_idx = 0
        self.manual_data = None
        self.manual_nodes = [] # List of dicts
        self.manual_idx = 0
        
        # Viewer State
        self.viewer_content = [] # List of lines
        self.viewer_scroll = 0
        self.viewer_path = ""
        self.viewer_title = ""

    def load_registry(self):
        try:
            # Assume manual.json is in docs/manual/
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            manual_json = os.path.join(root_dir, "docs", "manual", "manual.json")
            
            if os.path.exists(manual_json):
                with open(manual_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Data is a list of items
                    self.manual_nodes = []
                    for item in data:
                        self.manual_nodes.append({
                            "title": item.get("title", "Untitled"),
                            "desc": item.get("description", ""),
                            "file": item.get("file", ""),
                            "category": item.get("category", "General")
                        })
            else:
                self.manual_nodes = [{"title": "Error: manual.json missing", "desc": f"Path: {manual_json}", "file": "", "category": "Error"}]
        except Exception as e:
            self.manual_nodes = [{"title": "Error loading manual", "desc": str(e), "file": "", "category": "Error"}]

    def load_viewer_content(self, relative_path):
         try:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            full_path = os.path.join(root_dir, "docs", "manual", relative_path)
            
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.viewer_content = content.splitlines()
                    self.viewer_scroll = 0
                    self.viewer_path = full_path
            else:
                 self.viewer_content = [f"File not found: {relative_path}", f"Full path: {full_path}"]
         except Exception as e:
             self.viewer_content = [f"Error loading file: {e}"]

s_state = SettingsState()
# Load immediately so it's ready
s_state.load_registry()

# --- UI Renderers ---

def get_menu_text():
    options = ["Restart CLI", "Open Manual / Documentation"]
    lines = []
    lines.append(("", "\n Settings \n\n"))
    
    for i, opt in enumerate(options):
        if i == s_state.menu_idx:
            lines.append(("class:menu-selected", f" > {opt} \n"))
        else:
             lines.append(("class:menu-item", f"   {opt} \n"))
             
    return lines

def get_list_text():
    lines = []
    lines.append(("", " Documentation Index \n"))
    lines.append(("ansigray", " Press Enter to view. j/k to navigate. \n\n"))
    
    start = max(0, s_state.manual_idx - 10)
    end = start + 25
    
    for i in range(start, min(end, len(s_state.manual_nodes))):
        node = s_state.manual_nodes[i]
        
        style = ""
        prefix = "   "
        
        if i == s_state.manual_idx:
            style = "class:menu-selected"
            prefix = " > "
        else:
            style = "ansiwhite"
            
        # Title
        lines.append((style, f"{prefix}{node['title']}"))
        # Category (right aligned-ish or just parenthesized)
        lines.append(("ansigray", f" ({node['category']})\n"))
        
        # Description (if selected)
        if i == s_state.manual_idx:
             lines.append(("ansigray italic", f"      {node['desc']}\n"))
        
    return lines

def get_viewer_text():
    # Render visible lines based on scroll
    max_h = 40 # Approx height
    visible = s_state.viewer_content[s_state.viewer_scroll : s_state.viewer_scroll + max_h]
    
    lines = []
    # Header
    lines.append(("class:header", f" MANUAL: {s_state.viewer_title} \n"))
    lines.append(("ansigray", "-"*60 + "\n"))
    
    for line in visible:
        # Simple syntax highlighting based on Markdown
        if line.strip().startswith("#"):
             lines.append(("ansiyellow bold", line + "\n"))
        elif line.strip().startswith("-") or line.strip().startswith("*"):
             lines.append(("ansicyan", line + "\n"))
        elif "`" in line:
             # Basic regex for code could go here, simply coloring whole line for now
             lines.append(("ansigreen", line + "\n"))
        else:
             lines.append(("ansiwhite", line + "\n"))
             
    lines.append(("ansigray", "-"*60 + "\n"))
    lines.append(("ansigray", f" Line {s_state.viewer_scroll+1}/{len(s_state.viewer_content)} (j/k scroll, q/ESC exit) \n"))
    
    return lines

# --- Keybindings ---
kb = KeyBindings()

@kb.add('up')
@kb.add('w')
@kb.add('k')
def up(e):
    if s_state.mode == "MENU":
        s_state.menu_idx = max(0, s_state.menu_idx - 1)
    elif s_state.mode == "MANUAL":
        s_state.manual_idx = max(0, s_state.manual_idx - 1)
    elif s_state.mode == "VIEWER":
        s_state.viewer_scroll = max(0, s_state.viewer_scroll - 1)

@kb.add('down')
@kb.add('s')
@kb.add('j')
def down(e):
    if s_state.mode == "MENU":
        s_state.menu_idx = min(1, s_state.menu_idx + 1)
    elif s_state.mode == "MANUAL":
        s_state.manual_idx = min(len(s_state.manual_nodes)-1, s_state.manual_idx + 1)
    elif s_state.mode == "VIEWER":
        max_scroll = max(0, len(s_state.viewer_content) - 10)
        s_state.viewer_scroll = min(max_scroll, s_state.viewer_scroll + 1)

@kb.add('enter')
@kb.add('right')
@kb.add('d')
@kb.add('l')
def enter(e):
    if s_state.mode == "MENU":
        if s_state.menu_idx == 0:
            import os; import sys
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            s_state.mode = "MANUAL"
            s_state.load_registry()
            
    elif s_state.mode == "MANUAL":
        # Open Viewer
        if s_state.manual_nodes:
            node = s_state.manual_nodes[s_state.manual_idx]
            if node["file"]:
                s_state.viewer_title = node["title"]
                s_state.load_viewer_content(node["file"])
                s_state.mode = "VIEWER"

@kb.add('left')
@kb.add('a')
@kb.add('h')
@kb.add('escape')
@kb.add('q') # Quit viewer
def back(e):
    if s_state.mode == "VIEWER":
        s_state.mode = "MANUAL"
    elif s_state.mode == "MANUAL":
        s_state.mode = "MENU"
    elif s_state.mode == "MENU":
         state.active_focus_zone = "SIDEBAR"
         e.app.layout.focus_previous()

# Quick Jumps
@kb.add('g', 'g')
def top(e):
    if s_state.mode == "VIEWER": s_state.viewer_scroll = 0

@kb.add('G')
def bottom(e):
     if s_state.mode == "VIEWER":
         s_state.viewer_scroll = max(0, len(s_state.viewer_content) - 20)

# --- Layout ---

from prompt_toolkit.layout.containers import DynamicContainer

def get_body():
    if s_state.mode == "MENU":
        return Window(content=FormattedTextControl(get_menu_text, key_bindings=kb, focusable=True), style="class:launcher-content")
    elif s_state.mode == "MANUAL":
        return Window(content=FormattedTextControl(get_list_text, key_bindings=kb, focusable=True), style="class:launcher-content")
    elif s_state.mode == "VIEWER":
        return Window(content=FormattedTextControl(get_viewer_text, key_bindings=kb, focusable=True), style="class:launcher-content")

layout = Frame(
    body=DynamicContainer(get_body),
    title=" Settings & Documentation ",
    style="class:gold-frame"
)
