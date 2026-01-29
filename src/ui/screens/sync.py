from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Label, Frame
from prompt_toolkit.key_binding import KeyBindings
from ui.state import state
from core.sync import check_sync_status, fix_all_issues

def refresh():
    state.sync_issues = check_sync_status()

def fix(e=None):
    fix_all_issues()
    refresh()
    state.set_status("Fixed all sync issues.")

def get_sync_text():
    if not state.sync_issues:
        return " All Systems Standard. "
    lines = []
    for issue in state.sync_issues:
        lines.append(('class:error', f" {issue['status']} "))
        lines.append(('', f" {issue['file']} : {issue['details']}\n"))
    return lines

kb_sync = KeyBindings()
kb_sync.add('f9')(fix)

layout = Frame(
    body=HSplit([
        Label(" SYNC DASHBOARD (F9 to Fix All) "),
        Window(content=FormattedTextControl(get_sync_text, key_bindings=kb_sync, focusable=True, show_cursor=False))
    ]),
    title=" Sync ",
    style="class:gold-frame"
)
