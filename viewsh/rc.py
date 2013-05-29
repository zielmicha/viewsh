from viewsh import terminal
from viewsh.prompt import PS1

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

def default_rc(state):
    state[PS1] = '{cyan}{path}{reset} {red}{bold}${reset} '
