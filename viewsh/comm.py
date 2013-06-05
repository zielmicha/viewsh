import socket
import os
import pickle

from viewsh import state

class Interface(object):
    def __init__(self):
        self._path = os.environ.get('VIEWSH_SOCKET')

    def _connect(self):
        sock = socket.socket(socket.AF_UNIX)
        sock.connect(self._path)
        return sock

    def _call(self, data):
        sock = self._connect()
        f = sock.makefile('r+')
        pickle.dump(data, f)
        f.flush()
        return pickle.load(f)

    def is_connected(self):
        return bool(self._path)

    def patch_log(self):
        # set local viewsh.log to remote function
        import viewsh.tools
        viewsh.tools._log_real = self.log

    def __getattr__(self, name):
        def call(*args, **kwargs):
            if self._path:
                return self._call([name, args, kwargs])
            else:
                return None

        return call

class World(state.State):
    pass
