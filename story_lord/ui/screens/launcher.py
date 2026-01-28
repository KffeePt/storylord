import shutil
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Label, Frame
from prompt_toolkit.key_binding import KeyBindings
import os
from ui.screens import dashboard
from ui.state import state
from core.config import set_story_root, STORY_LORD_ROOT, ensure_global_root

# UI States: "MENU", "DELETE_CONFIRM", "CREATE_INPUT"
launcher_mode = "MENU"
menu_idx = 0
story_options = []
target_val = None # Logic holder
input_buffer = "" # Logic holder for naming

def refresh_stories():
    global story_options
    ensure_global_root()
    story_options = []
    
    try:
        items = os.listdir(STORY_LORD_ROOT)
        # Sort folders
        items.sort()
        for item in items:
            item_path = os.path.join(STORY_LORD_ROOT, item)
            if os.path.isdir(item_path):
                 story_options.append({"label": f"Open: {item}", "action": "open", "val": item})
    except Exception as e:
        state.set_status(f"Error scanning global root: {e}")

    story_options.append({"label": "Create New Story", "action": "create", "val": None})
    story_options.append({"label": "Exit", "action": "exit", "val": None})

def get_menu_text():
    if launcher_mode == "DELETE_CONFIRM":
        return [
            ("", "\n\n"),
            ("class:header", " DELETE STORY? \n\n"),
            ("class:warning", f" Are you sure you want to delete '{target_val}'?\n"),
            ("class:error", " This action cannot be undone.\n\n"),
            ("", " [Y] Yes   [N] No "),
        ]
    elif launcher_mode == "CREATE_INPUT":
         return [
            ("", "\n\n"),
            ("class:header", " NEW STORY \n\n"),
            ("", " Enter Story Name: "),
            ("class:menu-selected", f"{input_buffer}_\n\n"),
            ("", " [Enter] Confirm   [Esc] Cancel "),
        ]
    
    # Normal Menu
    lines = []
    lines.append(("", "\n"))
    lines.append(("class:header", "  STORY LORD v3  \n"))
    lines.append(("", f"  Storage: {STORY_LORD_ROOT}\n\n"))
    
    for i, opt in enumerate(story_options):
        prefix = " > " if i == menu_idx else "   "
        style = "class:menu-selected" if i == menu_idx else "class:menu-item"
        lines.append((style, f"{prefix}{opt['label']}\n"))
    
    # Help text footer
    if story_options and story_options[menu_idx]["action"] == "open":
         lines.append(("", "\n [Delete] Remove Story"))
        
    return lines

from prompt_toolkit.keys import Keys

# ... (imports)

def handle_menu_input(event):
    global menu_idx, launcher_mode, target_val, input_buffer
    key = event.key_sequence[0].key
    
    if key == Keys.Up:
        menu_idx = max(0, menu_idx - 1)
    elif key == Keys.Down:
        menu_idx = min(len(story_options)-1, menu_idx + 1)
    elif key == Keys.Delete:
        if story_options[menu_idx]["action"] == "open":
            target_val = story_options[menu_idx]["val"]
            launcher_mode = "DELETE_CONFIRM"
    elif key == Keys.Enter:
        opt = story_options[menu_idx]
        if opt["action"] == "open":
            set_story_root(opt["val"]) 
            # Recalculate full path carefully
            ensure_global_root()
            path = os.path.join(STORY_LORD_ROOT, opt["val"])
            state.load_story(path)
            state.active_screen = "DASHBOARD"
            
            # Reset focus to sidebar?
            # Since sidebar is the first focusable element in the main layout VSplit, 
            # we might just let prompt_toolkit find it, or force focus on the app (which resets to root?).
            # Let's try explicit focusing if we can find it, otherwise rely on layout order.
            # But the layout is dynamic. 
            # Ideally we want to focus the Sidebar.
            # The sidebar window doesn't have a global reference. 
            # We can try to traverse or just use focus_next()?
            # Let's NOT force focus on dashboard.layout.
            pass
            
        elif opt["action"] == "create":
            input_buffer = ""
            launcher_mode = "CREATE_INPUT"
        elif opt["action"] == "exit":
            event.app.exit()

def handle_delete_input(event):
    global launcher_mode
    # data is the actual character typed, key might be 'y' or similar
    key = event.key_sequence[0].key
    char = event.data
    
    if char and char.lower() == 'y':
        # Delete
        try:
            path = os.path.join(STORY_LORD_ROOT, target_val)
            shutil.rmtree(path)
            state.set_status(f"Deleted {target_val}")
        except Exception as e:
            state.set_status(f"Error deleting: {e}")
        refresh_stories()
        launcher_mode = "MENU"
        
    elif (char and char.lower() == 'n') or key == Keys.Escape:
        launcher_mode = "MENU"

def handle_create_input(event):
    global launcher_mode, input_buffer
    key = event.key_sequence[0].key
    
    if key == Keys.Enter:
        if not input_buffer.strip(): return
        # Create
        try:
            name = input_buffer.strip().replace(" ", "_")
            path = os.path.join(STORY_LORD_ROOT, name)
            if os.path.exists(path):
                 state.set_status("Error: Story already exists")
            else:
                os.makedirs(path)
                # Create specs folder structure
                os.makedirs(os.path.join(path, "specs"))
                state.set_status(f"Created {name}")
                refresh_stories()
                launcher_mode = "MENU"
        except Exception as e:
            state.set_status(f"Error creating: {e}")
            
    elif key == Keys.Escape:
        launcher_mode = "MENU"
    elif key == Keys.Backspace:
        input_buffer = input_buffer[:-1]
    else:
        # Append typed character
        if event.data and len(event.data) == 1:
             input_buffer += event.data

kb = KeyBindings()
@kb.add('<any>')
def _handler(event):
    if launcher_mode == "MENU":
        handle_menu_input(event)
    elif launcher_mode == "DELETE_CONFIRM":
        handle_delete_input(event)
    elif launcher_mode == "CREATE_INPUT":
        handle_create_input(event)

# Initial load
refresh_stories()

# Frame style will be defined in app.py
layout = Frame(
    body=Window(
        content=FormattedTextControl(get_menu_text, key_bindings=kb, focusable=True, show_cursor=False),
        align=WindowAlign.CENTER,
        style="class:launcher-content",
        wrap_lines=False,
    ),
    title=" Story Lord ",
    style="class:gold-frame"
)
