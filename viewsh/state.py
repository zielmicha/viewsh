from viewsh import comm
from viewsh.transport import local

class ShellState(object):
    '''
    Class that keeps track of state of anything.
    It's job is to switch between settings set on events
    like connection to remote server.
    '''

    def __init__(self):
        self.history = []
        self.interface = comm.Interface()
        self.interface.log('ShellState init')
        self.interface.patch_log()
        self.transport = local.LocalTransport()
        self.current_directory = '/'
