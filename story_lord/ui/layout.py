from prompt_toolkit.layout.containers import VSplit, HSplit, Window, DynamicContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, Label, Box
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.application.current import get_app

from ui.state import state
# Screen layouts are imported in app.py or by registry. 
# We need to access them to focus. 
# Circular imports are tricky. We'll rely on get_app().layout.current_window or standard names if possible.
# Actually, create_layout is called by app, which has imported screens. 
# We can use a global registry or passed in mapping.
SCREENS = {}

MENU_ITEMS = ["DASHBOARD", "GENERATOR", "EXPLORER", "SYNC"]

def get_sidebar_text():
    # Renders the sidebar
    # We highlight the active one.
    # If sidebar has focus, maybe make it brighter? 
    # For now, standard selected style.
    lines = []
    for item in MENU_ITEMS:
        if state.active_screen == item:
             lines.append(('class:menu-selected', f" > {item} \n"))
        else:
             lines.append(('class:sidebar-item', f"   {item} \n"))
    lines.append(('', '\n [Q] Quit'))
    return lines

# Sidebar KeyBindings
kb_sidebar = KeyBindings()

@kb_sidebar.add('up')
@kb_sidebar.add('w') 
def _up(e):
    try:
        idx = MENU_ITEMS.index(state.active_screen)
        new_idx = max(0, idx - 1)
        state.active_screen = MENU_ITEMS[new_idx]
    except ValueError:
        pass

@kb_sidebar.add('down')
@kb_sidebar.add('s')
def _down(e):
    try:
        idx = MENU_ITEMS.index(state.active_screen)
        new_idx = min(len(MENU_ITEMS) - 1, idx + 1)
        state.active_screen = MENU_ITEMS[new_idx]
    except ValueError:
        pass

@kb_sidebar.add('right')
@kb_sidebar.add('d')
@kb_sidebar.add('enter')
def _enter_content(e):
    # Focus the content area
    # We need to find the Window of the active screen.
    # Since DynamicContainer uses the SCREENS dict, we can try to find the focusable window in that layout.
    target_layout = SCREENS.get(state.active_screen)
    if target_layout:
        e.app.layout.focus(target_layout)

def get_content_container():
    # Returns the container for the active screen
    return SCREENS.get(state.active_screen, Window(align="center", content=FormattedTextControl("Screen Not Found")))

def create_layout():
    # Sidebar
    sidebar_control = FormattedTextControl(get_sidebar_text, key_bindings=kb_sidebar, show_cursor=False, focusable=True)
    sidebar = Box(
        body=Window(content=sidebar_control, width=15),
        padding=1,
        style='class:sidebar'
    )
    
    # Header
    header = Window(height=1, content=FormattedTextControl(
        lambda: f" STORY LORD v3 | {state.status_message} ", style='class:header'
    ))
    
    # Main Content Area (Dynamic)
    content_area = DynamicContainer(get_content_container)
    
    # Conditional Layout
    def get_root_container():
        if not state.is_story_loaded:
            # Launcher Layout (Simple Centered)
            return DynamicContainer(get_content_container)
        else:
            # Main App Layout (Header + Sidebar + Content)
            return HSplit([
               header,
               VSplit([
                   sidebar,
                   content_area
               ])
           ])
    
    return DynamicContainer(get_root_container)
