from prompt_toolkit.layout.containers import VSplit, Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
import os

# Settings State
class SettingsState:
    def __init__(self):
        self.mode = "MENU" # MENU, MANUAL
        self.menu_idx = 0
        self.manual_path = None # Current doc path
        self.manual_nodes = [] # List of (display_name, path, is_dir, level)
        self.manual_idx = 0
        self.manual_content = "Select a document..."

    def build_tree(self):
        self.manual_nodes = []
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")) # src/ui/screens -> src/ui -> src -> root
        docs_dir = os.path.join(root_dir, "docs")
        readme = os.path.join(root_dir, "README.md")
        
        # Add README
        if os.path.exists(readme):
             self.manual_nodes.append(("MANUAL (README)", readme, False, 0))
             
        # Add Docs
        if os.path.exists(docs_dir):
            for root, dirs, files in os.walk(docs_dir):
                level = root.replace(docs_dir, "").count(os.sep) + 1
                basename = os.path.basename(root)
                if basename == "docs": continue 
                
                self.manual_nodes.append((f"[{basename}]", root, True, level))
                
                for f in files:
                    if f.endswith(".md"):
                        self.manual_nodes.append((f, os.path.join(root, f), False, level + 1))

s_state = SettingsState()
s_state.build_tree()

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

def get_tree_text():
    lines = []
    lines.append(("", " Documentation Tree \n\n"))
    
    start = max(0, s_state.manual_idx - 10)
    end = start + 20
    
    for i in range(start, min(end, len(s_state.manual_nodes))):
        name, path, is_dir, level = s_state.manual_nodes[i]
        indent = "  " * level
        style = ""
        prefix = "   "
        
        if i == s_state.manual_idx:
            style = "class:menu-selected"
            prefix = " > "
            
        icon = "[+]" if is_dir else " - "
        lines.append((style, f"{prefix}{indent}{icon} {name} \n"))
        
    return lines

def get_content_text():
    return s_state.manual_content

kb = KeyBindings()

@kb.add('up')
@kb.add('w')
def up(e):
    if s_state.mode == "MENU":
        s_state.menu_idx = max(0, s_state.menu_idx - 1)
    else:
        s_state.manual_idx = max(0, s_state.manual_idx - 1)
        load_content()

@kb.add('down')
@kb.add('s')
def down(e):
    if s_state.mode == "MENU":
        s_state.menu_idx = min(1, s_state.menu_idx + 1)
    else:
        s_state.manual_idx = min(len(s_state.manual_nodes)-1, s_state.manual_idx + 1)
        load_content()

def load_content():
    if not s_state.manual_nodes: return
    name, path, is_dir, level = s_state.manual_nodes[s_state.manual_idx]
    if is_dir:
        s_state.manual_content = f"\n Folder: {name}\n Path: {path}"
    else:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                s_state.manual_content = f.read()
        except Exception as e:
            s_state.manual_content = str(e)

@kb.add('enter')
@kb.add('right')
@kb.add('d')
def enter(e):
    if s_state.mode == "MENU":
        if s_state.menu_idx == 0:
            # Restart
            import os
            import sys
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Manual
            s_state.mode = "MANUAL"
            load_content()
    else:
        # In Manual mode, maybe enter expands folder? (Not imp yet)
        pass

@kb.add('left')
@kb.add('a')
def back(e):
    if s_state.mode == "MANUAL":
        s_state.mode = "MENU"
    else:
        # Back to Sidebar
        state.active_focus_zone = "SIDEBAR"
        e.app.layout.focus_previous()

menu_control = FormattedTextControl(get_menu_text, key_bindings=kb, focusable=True)
tree_control = FormattedTextControl(get_tree_text)
content_control = FormattedTextControl(get_content_text)

# Dynamic Layout based on mode
def get_layout():
    if s_state.mode == "MENU":
         return Window(content=menu_control, style="class:launcher-content")
    else:
         return VSplit([
             Window(content=tree_control, width=40, style="class:launcher-content", key_bindings=kb), # Keybindings here?
             Window(width=1, char="|", style="class:line"),
             Window(content=content_control, style="class:launcher-content", wrap_lines=True)
         ])
         
# We need keybindings on the ACTIVE window.
# In Manual mode, tree_control should be focused.
# But layout structure changes.
# Simplest: Always VSplit, but hide tree if in menu? 
# Or just use Frame with Dynamic Body.
from prompt_toolkit.layout.containers import DynamicContainer
def get_body():
    if s_state.mode == "MENU":
        return Window(content=menu_control, style="class:launcher-content")
    else:
        # We need to attach bindings to the tree control for navigation
        # PTK bindings are attached to controls.
        # reusing KB is fine.
        return VSplit([
             Window(content=FormattedTextControl(get_tree_text, key_bindings=kb, focusable=True), width=40, style="class:launcher-content"),
             Window(width=1, char="|", style="class:line"),
             Window(content=content_control, style="class:launcher-content", wrap_lines=True)
         ])

layout = Frame(
    body=DynamicContainer(get_body),
    title=" Settings & Documentation ",
    style="class:gold-frame"
)
