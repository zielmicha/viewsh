from viewsh.tools import log
from viewsh import terminal
from viewsh.prompt import PS1
from viewsh.executor import Executor
from viewsh.transport import Transport
from viewsh.shell import CurrentDirectory, SwitchTransport, EnvCache, \
    History

import os

HISTORY_PATH = os.path.expanduser('~/.viewsh_history')

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
    state[PS1] = '{red}{user}{yellow}@{cyan}{host}{reset} {red}{path} {bold}${reset} '
    state[Executor].aliases.update({
        'ls': 'ls --color',
        '..': 'cd ..',
        'py': 'ipython3 --no-confirm-exit --no-banner',
        'gs': 'git status',
    })
    state[SwitchTransport].save_fields.append(CurrentDirectory)
    state[SwitchTransport].switch_hook.add(on_new_transport)
    load_history(state[History])
    state[History].modify_hook.add(on_history_modified)

    from viewsh import commands
    commands.register(state)

def on_new_transport(state, old_values):
    state[CurrentDirectory] = state[EnvCache].environ.get('HOME', '/')

def load_history(history):
    try:
        f = open(HISTORY_PATH)
    except IOError:
        return
    for line in f:
        list.append(history, line.strip())

def on_history_modified(history):
    try:
        f = open(HISTORY_PATH + '.tmp', 'w')
        for item in history:
            f.write(item + '\n')
        f.close()
        os.rename(HISTORY_PATH + '.tmp', HISTORY_PATH)
    except (IOError, OSError) as err:
        log('writing history failed %r' % err)

def main():
    # Assemble everything.
    from viewsh import terminal
    from viewsh import rc
    from viewsh import state as shell_state
    from viewsh.transport import local
    from viewsh import comm
    from viewsh import edit
    from viewsh import prompt

    terminal = terminal.Terminal()
    terminal.start()
    state = shell_state.ShellState()
    state[SwitchTransport].switch(local.LocalTransport())
    state[comm.Interface].patch_log()
    setup(state)
    prompt = prompt.Prompt(state, terminal)

    while True:
        prompt.show()
        line_edit = edit.LineEdit(state, terminal)
        line = line_edit.prompt()
        state[Executor].execute(terminal, line)

if __name__ == '__main__':
    main()