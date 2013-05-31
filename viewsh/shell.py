from viewsh import comm
from viewsh.transport import Transport
from viewsh import terminal

class EnvCache(object):
    pass_state = True

    def __init__(self, state):
        self.state = state
        self._environ = None
        self.cache_for = None

    @property
    def environ(self):
        if self.state[Transport] != self.cache_for:
            self._environ = self.state[Transport].get_environ()
            self.cache_for = self.state[Transport]
        return self._environ

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
