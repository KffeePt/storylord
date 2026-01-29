from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Label, Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from core.metadata import scan_and_sync, load_all_metadata

metadata_cache = {}

# Fixed Order as requested
FIXED_CATEGORIES = [
    "Storyboard",
    "Characters",
    "Lore",
    "Canon",
    "Rules",
    "Composition",
    # Others can be appended if found
]

def refresh():
    global metadata_cache
    scan_and_sync()
    data = load_all_metadata()
    metadata_cache = data
    
    # Reset to categories if we are just opening or refreshing top level
    # But if we are deep, maybe keep context? 
    # For now, simplistic refresh updates counts.
    pass

def get_category_counts():
    counts = {cat: 0 for cat in FIXED_CATEGORIES}
    
    # helper
    all_specs = metadata_cache.specs if metadata_cache else {}
    
    # Dynamic categories from FS that aren't fixed?
    # For now strict adherence to user request "make the explorer have this spec folder structure constant"
    
    for path, spec in all_specs.items():
        cat = spec.category
        if cat in counts:
            counts[cat] += 1
        else:
            # If we want to show others
            counts[cat] = counts.get(cat, 0) + 1
            
    return counts

def get_files_in_category(cat):
    all_specs = metadata_cache.specs if metadata_cache else {}
    files = []
    for path, spec in all_specs.items():
        if spec.category == cat:
            files.append(path)
    return sorted(files)

def get_list_text():
    lines = []
    
    if state.exp_mode == "CATEGORIES":
        counts = get_category_counts()
        
        # Merge FIXED with any others found (optional, but good for robustness)
        display_cats = list(FIXED_CATEGORIES)
        for c in counts:
             if c not in display_cats:
                 display_cats.append(c)
                 
        start = max(0, state.exp_selected_idx - 10)
        end = start + 20
        
        state.exp_files = display_cats # Hack: reusing exp_files to store list for index bounds
        
        for i in range(start, min(end, len(display_cats))):
            cat = display_cats[i]
            count = counts.get(cat, 0)
            
            count_str = f"({count} files)" if count > 0 else "(no files)"
            
            if cat == "Storyboard":
                 # Special styling for Storyboard
                 if i == state.exp_selected_idx:
                      style = "class:special-storyboard"
                 else:
                      style = "class:warning" # Distinguish it even when not selected
            else:
                 style = "class:menu-selected" if i == state.exp_selected_idx else ""
            
            lines.append((style, f" {cat} {count_str} \n"))

    elif state.exp_mode == "FILES":
         # state.exp_files should have been set when entering
         if not state.exp_files:
             return [("", " (Empty Folder) ")]
             
         start = max(0, state.exp_selected_idx - 10)
         end = start + 20
         
         for i in range(start, min(end, len(state.exp_files))):
            f = state.exp_files[i]
            style = "class:menu-selected" if i == state.exp_selected_idx else ""
            lines.append((style, f" {f} \n"))
            
    return lines

def get_meta_text():
    if state.exp_mode == "CATEGORIES":
        return " Select a category... "
        
    if not state.exp_files: return ""
    fname = state.exp_files[state.exp_selected_idx]
    meta = metadata_cache.specs.get(fname, None)
    if not meta: return " No Metadata "
    return f"Title: {meta.title}\nVer: {meta.version}\nDesc: {meta.description}"

kb_exp = KeyBindings()

@kb_exp.add('up')
@kb_exp.add('w')
def up(e): 
    # Bounds check based on mode
    if state.exp_mode == "CATEGORIES":
        limit = len(FIXED_CATEGORIES) # Approximate, reusing dynamic logic better
        # Actually we need the real list length.
        # Re-calc counts? optimized:
        # We rely on render to update state.exp_files? No that's risky.
        # Let's calculate list len properly
        counts = get_category_counts()
        display_cats = list(FIXED_CATEGORIES)
        for c in counts:
             if c not in display_cats: display_cats.append(c)
        limit = len(display_cats)
        state.exp_selected_idx = max(0, state.exp_selected_idx - 1)
        
    else:
        state.exp_selected_idx = max(0, state.exp_selected_idx - 1)

@kb_exp.add('down')
@kb_exp.add('s')
def down(e): 
    if state.exp_mode == "CATEGORIES":
        counts = get_category_counts()
        display_cats = list(FIXED_CATEGORIES)
        for c in counts:
             if c not in display_cats: display_cats.append(c)
        state.exp_selected_idx = min(len(display_cats)-1, state.exp_selected_idx + 1)
    else:
        state.exp_selected_idx = min(len(state.exp_files)-1, state.exp_selected_idx + 1)

@kb_exp.add('enter')
@kb_exp.add('right')
@kb_exp.add('d')
def enter(e):
    if state.exp_mode == "CATEGORIES":
        # Enter Category
        counts = get_category_counts()
        display_cats = list(FIXED_CATEGORIES)
        for c in counts:
             if c not in display_cats: display_cats.append(c)
             
        selected_cat = display_cats[state.exp_selected_idx]
        
        if selected_cat == "Storyboard":
             # Route to Storyboard Screen
             from ui.screens import storyboard
             state.active_screen = "STORYBOARD"
             e.app.layout.focus(storyboard.layout)
             return
        
        # Switch mode
        state.exp_mode = "FILES"
        state.exp_category = selected_cat
        state.exp_files = get_files_in_category(selected_cat)
        state.exp_selected_idx = 0

@kb_exp.add('left')
@kb_exp.add('a')
def back(e):
    if state.exp_mode == "FILES":
        state.exp_mode = "CATEGORIES"
        state.exp_category = None
        state.exp_selected_idx = 0 # Or try to remember previous? 0 is fine.
    else:
        # Back to Sidebar
        state.active_focus_zone = "SIDEBAR"
        e.app.layout.focus_previous()

layout = Frame(
    body=HSplit([
        Label(" EXPLORER (WASD/Arrows) "),
        VSplit([
            Frame(Window(content=FormattedTextControl(get_list_text, key_bindings=kb_exp, focusable=True, show_cursor=False))),
            Frame(Window(content=FormattedTextControl(get_meta_text, show_cursor=False)))
        ])
    ]),
    title=" Explorer ",
    style="class:gold-frame"
)
