from viewsh import comm
from viewsh.transport import local

import posixpath

class ShellState(object):
    def __init__(self):
        self.history = []
        self.interface = comm.Interface()
        self.interface.log('ShellState init')
        self.interface.patch_log()
        self.transport = local.LocalTransport()
        self.current_directory = '/'

    def chdir(self, path):
        new_dir = posixpath.join(self.current_directory, path)
        self.current_directory = self.transport.real_path(new_dir)
