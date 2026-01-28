from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.widgets import Label, Frame, Button
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from core.generator import generate_spec
from core.config import CATEGORIES

# Buffers
title_buffer = Buffer()
desc_buffer = Buffer()

def get_cat_text():
    return f"< {CATEGORIES[state.gen_cat_idx]} >"

def prev_cat():
    state.gen_cat_idx = (state.gen_cat_idx - 1) % len(CATEGORIES)
def next_cat():
    state.gen_cat_idx = (state.gen_cat_idx + 1) % len(CATEGORIES)

def do_generate(event=None):
    cat = CATEGORIES[state.gen_cat_idx]
    title = title_buffer.text.strip()
    if not title:
        state.set_status("Error: Title Missing")
        return
    success, msg = generate_spec(cat, title, description=desc_buffer.text)
    state.set_status(msg)
    if success:
        title_buffer.text = ""
        desc_buffer.text = ""

# Controls
cat_control = FormattedTextControl(get_cat_text, show_cursor=False)
kb_gen = KeyBindings()
kb_gen.add('left')(lambda e: prev_cat())
kb_gen.add('right')(lambda e: next_cat())
kb_gen.add('f9')(do_generate)
cat_control.key_bindings = kb_gen

layout = Frame(
    body=HSplit([
        Label(" SPEC GENERATOR "),
        Label("Category [Left/Right]:"),
        Window(height=1, content=cat_control),
        Label("Title:"),
        Frame(Window(height=1, content=BufferControl(title_buffer))),
        Label("Description:"),
        Frame(Window(height=3, content=BufferControl(desc_buffer))),
        Label("Press [F9] to Generate"),
    ]),
    title=" Generator ",
    style="class:gold-frame"
)
