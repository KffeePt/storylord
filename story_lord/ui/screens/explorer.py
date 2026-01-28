from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.widgets import Label, Frame
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from core.metadata import scan_and_sync, load_all_metadata

metadata_cache = {}

def refresh():
    global metadata_cache
    scan_and_sync()
    data = load_all_metadata()
    metadata_cache = data
    state.exp_files = sorted(list(data.specs.keys()))

def get_list_text():
    lines = []
    if not state.exp_files: return " (No Files) "
    start = max(0, state.exp_selected_idx - 10)
    end = start + 20
    
    for i in range(start, min(end, len(state.exp_files))):
        f = state.exp_files[i]
        style = "class:menu-selected" if i == state.exp_selected_idx else ""
        lines.append((style, f" {f} \n"))
    return lines

def get_meta_text():
    if not state.exp_files: return ""
    fname = state.exp_files[state.exp_selected_idx]
    meta = metadata_cache.specs.get(fname, None)
    if not meta: return " No Metadata "
    return f"Title: {meta.title}\nVer: {meta.version}\nDesc: {meta.description}"

kb_exp = KeyBindings()
@kb_exp.add('up')
def up(e): state.exp_selected_idx = max(0, state.exp_selected_idx - 1)
@kb_exp.add('down')
def down(e): state.exp_selected_idx = min(len(state.exp_files)-1, state.exp_selected_idx + 1)

layout = Frame(
    body=HSplit([
        Label(" EXPLORER (Up/Down) "),
        VSplit([
            Frame(Window(content=FormattedTextControl(get_list_text, key_bindings=kb_exp, focusable=True, show_cursor=False))),
            Frame(Window(content=FormattedTextControl(get_meta_text, show_cursor=False)))
        ])
    ]),
    title=" Explorer ",
    style="class:gold-frame"
)
