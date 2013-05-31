
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
            if getattr(key, 'pass_state', False):
                val = key(self)
            else:
                val = key()
            self._store[key] = val

        return self._store[key]

    def __setitem__(self, key, val):
        assert isinstance(key, type)
        self._store[key] = val

    def __contains__(self, key):
        return key in self._store

class Hook(object):
    def __init__(self, reduce=None, default=None):
        self._funcs = []
        self._reduce = reduce
        self._default = default

    def add(self, func):
        self._funcs.append(func)

    def call(self, *args, **kwargs):
        val = []
        for func in self._funcs:
            val.append(func(*args, **kwargs))
        if self._reduce:
            return reduce(self._reduce, val, self._default)
        else:
            return val
