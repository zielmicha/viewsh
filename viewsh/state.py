from viewsh import comm
from viewsh.transport import local
from viewsh import terminal

class ShellState(object):
    '''
    Class that keeps track of state of anything.
    It is essentialy dictionary which keys are types.
    '''

    def __init__(self):
        self._store = {}

    def __getitem__(self, key):
        assert isinstance(key, type)
        if key not in self._store:
            val = key()
            self._store[key] = val

        return self._store[key]

    def __setitem__(self, key, val):
        assert isinstance(key, type)
        self._store[key] = val

class History(object):
    def __new__(cls):
        return []

class CurrentDirectory(object):
    def __new__(cls):
        return '/'

def default_format_params(src=None):
    params = dict(src)
    params.update(terminal.Color.__dict__)
    return params

def format_with_default_params(txt, **kwargs):
    return txt.format(**default_format_params(kwargs))
