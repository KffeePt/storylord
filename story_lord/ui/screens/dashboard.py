from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from ui.menu import MenuManager
from ui.screens import generator, explorer, sync

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
        "children": ["NAV_GEN", "NAV_EXP", "NAV_SYNC"],
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
    elif action_param in ["GENERATOR", "EXPLORER", "SYNC"]:
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

def get_menu_render():
    node = menu_mgr.get_current_node()
    children = menu_mgr.get_children()
    
    lines = []
    
    # Path / Title
    lines.append(("class:header", f" {node.label} \n"))
    lines.append(("", f" {node.description}\n\n"))
    
    # Breadcrumbs (Simple)
    path_str = " > ".join(menu_mgr.history + [menu_mgr.curr_id])
    lines.append(("class:warning", f" Path: {path_str}\n\n"))

    # Children
    for i, child in enumerate(children):
        if i == menu_mgr.selected_idx:
            lines.append(("class:menu-selected", f" > {child.label} \n"))
        else:
            lines.append(("class:menu-item", f"   {child.label} \n"))
            
    return lines

kb = KeyBindings()
@kb.add('up')
@kb.add('w')
def _up(e): menu_mgr.navigate_up()

@kb.add('down')
@kb.add('s')
def _down(e): menu_mgr.navigate_down()

@kb.add('right')
@kb.add('d')
@kb.add('enter')
def _enter(e):
    action = menu_mgr.enter_child()
    if action:
        execute_action(action)

@kb.add('left')
@kb.add('a')
def _back(e): 
    # Check if we can go back in menu
    if menu_mgr.history:
        menu_mgr.go_back()
    else:
        # We are at root, go back to sidebar
        # We need to find the sidebar window. 
        # In a HSplit/VSplit, we can use focus_previous checks? 
        # Easier: Focus the sidebar Logic.
        # But we don't have direct ref to sidebar object here easily without imports cycle.
        # HACK: Traverse layout or standard focus_previous?
        # Sidebar is usually "before" content in VSplit.
        e.app.layout.focus_previous()

layout = Frame(
    body=Window(
        content=FormattedTextControl(get_menu_render, key_bindings=kb, focusable=True, show_cursor=False),
        align=WindowAlign.CENTER,
        style="class:launcher-content",
        wrap_lines=False,
    ),
    title=" Dashboard ",
    style="class:gold-frame"
)
