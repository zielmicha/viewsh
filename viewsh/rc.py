from viewsh import terminal

import os

def setup(state):
    globals = {
        'state': state
    }
    default_rc(state)
    for path in get_rc_paths():
        if os.path.exists(path):
            execfile(path, globals)

def get_rc_paths():
    return [
        os.path.expanduser('~/.config/viewsh/rc.py'),
        '/etc/viewsh.rc.py']

def default_format_params(src=None):
    params = dict(src)
    params.update(terminal.Color.__dict__)
    return params

def format_with_default_params(txt, **kwargs):
    return txt.format(**default_format_params(kwargs))

def default_rc(state):
    state.ps1 = '{cyan}{path}{reset} {red}{bold}${reset} '
