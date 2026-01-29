from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from ui.menu import MenuManager
from ui.screens import generator, explorer, sync
import os

def dbg(msg):
    try:
        with open("dashboard_debug.txt", "a") as f:
            f.write(f"{str(msg)}\n")
    except:
        pass

# --- Menu Definition ---

# --- Menu Definition ---
DASHBOARD_MENU_TREE = {
    "ROOT": {
        "label": "Main Dashboard",
        "description": "Select an operation module.",
        "children": ["STORY_OPS", "SYSTEM_OPS"]
    },
    "STORY_OPS": {
        "label": "Story Operations",
        "description": "Manage content for the active story.",
        "children": ["NAV_GEN", "NAV_EXP", "NAV_STORY", "NAV_SYNC"],
        "props": {"section": "story"}
    },
    "SYSTEM_OPS": {
        "label": "System",
        "description": "Configuration and persistence.",
        "children": ["EXIT_APP"]
    },
    "NAV_GEN": {
        "label": "Spec Generator",
        "description": "Create new story specifications.",
        "param": "GENERATOR"
    },
    "NAV_EXP": {
        "label": "Explorer",
        "description": "View and manage file structure.",
        "param": "EXPLORER"
    },
    "NAV_STORY": {
        "label": "Storyboard (Timeline)",
        "description": "Visual Event Editor",
        "param": "STORYBOARD"
    },
    "NAV_SYNC": {
        "label": "Sync Status",
        "description": "Check metadata consistency.",
        "param": "SYNC"
    },
    "EXIT_APP": {
        "label": "Exit Story Lord",
        "description": "Close the application.",
        "param": "EXIT"
    }
}

menu_mgr = MenuManager(DASHBOARD_MENU_TREE)

def execute_action(action_param):
    if not action_param: return

    if action_param == "EXIT":
        from prompt_toolkit.application.current import get_app
        get_app().exit()
    elif action_param in ["GENERATOR", "EXPLORER", "SYNC", "STORYBOARD"]:
        # Switch screen
        state.active_screen = action_param
        
        from prompt_toolkit.application.current import get_app
        
        # Optional: Trigger refresh helper if needed
        if action_param == "GENERATOR":
             get_app().layout.focus(generator.layout)
             
        if action_param == "EXPLORER":
            explorer.refresh()
            get_app().layout.focus(explorer.layout)
            
        if action_param == "SYNC":
            sync.refresh()
            get_app().layout.focus(sync.layout)
            
        if action_param == "STORYBOARD":
            from ui.screens import storyboard
            storyboard.refresh()
            get_app().layout.focus(storyboard.layout)

def get_menu_render():
    node = menu_mgr.get_current_node()
    children = menu_mgr.get_children()
    
    lines = []
    
    # Check focus
    is_focused = (state.active_focus_zone == "CONTENT")
    if is_focused:
         pass # Good
    else:
         # Double check if we actually have PTK focus despite state sayng otherwise? 
         # No, rely on our state.
         pass

    # Path / Title
    lines.append(("class:header", f" {node.label} \n"))
    lines.append(("", f" {node.description}\n\n"))
    
    # Breadcrumbs (Simple)
    path_str = " > ".join(menu_mgr.history + [menu_mgr.curr_id])
    lines.append(("class:warning", f" Path: {path_str}\n\n"))

    # Children
    for i, child in enumerate(children):
        if i == menu_mgr.selected_idx:
            if is_focused:
                lines.append(("class:menu-selected", f" > {child.label} \n"))
            else:
                lines.append(("class:menu-item", f" > {child.label} \n")) # Standard style if not focused
        else:
            lines.append(("class:menu-item", f"   {child.label} \n"))
            
    return lines

from prompt_toolkit.keys import Keys

kb = KeyBindings()
@kb.add('<any>')
def _handler(event):
    key = event.key_sequence[0].key
    char = event.data
    
    # Debug
    # state.set_status(f"DBG: Key={key} Char={char}") # Too noisy?
    
    if key == Keys.Up or char == 'w':
        state.set_status("DEBUG: DASHBOARD UP/W (ANY)")
        try:
            menu_mgr.navigate_up()
        except Exception as ex:
            state.set_status(f"ERR: {ex}")
            
    elif key == Keys.Down or char == 's':
        state.set_status("DEBUG: DASHBOARD DOWN/S (ANY)")
        try:
            menu_mgr.navigate_down()
        except Exception as ex:
            state.set_status(f"ERR: {ex}")
            
    elif key == Keys.Right or key == Keys.Enter or char == 'd':
        state.set_status("DEBUG: DASHBOARD ENTER (ANY)")
        try:
            action = menu_mgr.enter_child()
            if action:
                execute_action(action)
        except Exception as ex:
            state.set_status(f"ERR: {ex}")
            
    elif key == Keys.Left or char == 'a':
        state.set_status("DEBUG: DASHBOARD BACK (ANY)")
        try:
            if menu_mgr.history:
                menu_mgr.go_back()
            else:
                state.set_status("DEBUG: Back to SIDEBAR")
                state.active_focus_zone = "SIDEBAR"
                event.app.layout.focus_previous()
        except Exception as ex:
            state.set_status(f"ERR: {ex}")

menu_control = FormattedTextControl(get_menu_render, key_bindings=kb, focusable=True, show_cursor=False)

# Restore Frame
from prompt_toolkit.widgets import Frame
layout = Frame(
    body=Window(
        content=menu_control,
        align=WindowAlign.CENTER,
        style="class:launcher-content",
        wrap_lines=False,
    ),
    title=" Dashboard ",
    style="class:gold-frame"
)
