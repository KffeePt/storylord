from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from core.metadata import load_all_metadata, scan_and_sync

# Local State
class StoryboardState:
    def __init__(self):
        self.nodes = [] # List of (filename, metadata)
        self.selected_idx = 0
        self.metadata_cache = None

sb_state = StoryboardState()

def refresh_data():
    try:
        scan_and_sync()
        data = load_all_metadata()
        sb_state.metadata_cache = data
        
        # Filter for Storyboard
        sb_state.nodes = []
        if data and data.specs:
            for path, spec in data.specs.items():
                if spec.category == "Storyboard":
                    sb_state.nodes.append((path, spec))
        
        # Sort nodes by filename for now
        sb_state.nodes.sort(key=lambda x: x[0])
        
        # Bounds check
        if sb_state.selected_idx >= len(sb_state.nodes):
            sb_state.selected_idx = max(0, len(sb_state.nodes) - 1)
            
    except Exception as e:
        state.set_status(f"Error loading storyboard: {e}")

def get_timeline_render():
    if not sb_state.nodes:
        return [("", "\n No Storyboard Nodes Found. \n Create files in 'Storyboard' folder. ")]
    
    lines = []
    lines.append(("", "\n")) # Padding
    
    # Draw Vertical Chain
    for i, (fname, spec) in enumerate(sb_state.nodes):
        title = spec.title if spec.title else fname
        
        # Selection Style
        prefix = "   "
        style = "class:menu-item"
        
        if i == sb_state.selected_idx:
            # Active Node
            style = "class:special-storyboard"
            prefix = " > "
            
        lines.append((style, f"{prefix}[ {title} ] \n"))
            
        # Arrow (unless last)
        if i < len(sb_state.nodes) - 1:
            if i == sb_state.selected_idx:
                 lines.append(("", "       |\n"))
                 lines.append(("", "       v\n"))
            else:
                 lines.append(("", "       |\n"))
                 lines.append(("", "       v\n"))
                 
    return lines

def get_detail_render():
    if not sb_state.nodes: return ""
    if sb_state.selected_idx >= len(sb_state.nodes): return ""
    
    fname, spec = sb_state.nodes[sb_state.selected_idx]
    
    text = []
    text.append(("class:header", f" {spec.title} \n"))
    text.append(("", f"\n File: {fname}\n"))
    text.append(("", f" Version: {spec.version}\n"))
    text.append(("", "-" * 40 + "\n"))
    text.append(("class:warning", f" Description:\n"))
    text.append(("", f"{spec.description}\n\n"))
    
    return text

kb = KeyBindings()

@kb.add('up')
@kb.add('w')
def move_up(event):
    if sb_state.selected_idx > 0:
        sb_state.selected_idx -= 1

@kb.add('down')
@kb.add('s')
def move_down(event):
    if sb_state.selected_idx < len(sb_state.nodes) - 1:
        sb_state.selected_idx += 1

@kb.add('r')
def refresh_binding(event):
    refresh_data()
    state.set_status("Refreshed Storyboard.")

@kb.add('q')
@kb.add('left')
@kb.add('a')
def exit_sb(event):
    # Back to Explorer
    state.active_screen = "EXPLORER"
    from ui.screens import explorer
    # Force explorer refresh just in case
    # explorer.refresh()
    event.app.layout.focus(explorer.layout)

menu_control = FormattedTextControl(get_timeline_render, key_bindings=kb, focusable=True)
detail_control = FormattedTextControl(get_detail_render)

layout = Frame(
    body=VSplit([
        Window(content=menu_control, width=40, style="class:launcher-content"),
        Window(width=1, char="|", style="class:line"),
        Window(content=detail_control, style="class:launcher-content")
    ]),
    title=" Storyboard Timeline ",
    style="class:gold-frame"
)

# Public refresh method called by app or other screens
def refresh():
    refresh_data()
