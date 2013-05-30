from abc import ABCMeta, abstractmethod
from viewsh.tools import shell_quote, as_utf8, log

class Transport(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, args, pty=True, size=None):
        '''
        Executes command specified as list args.
        '''

    @abstractmethod
    def execute_get_output(self, args):
        pass

    @abstractmethod
    def file_completions(self, path):
        pass

    @abstractmethod
    def real_path(self, path, need_dir):
        pass

class CommandBasedTransport(Transport):
    def file_completions(self, path, cwd='/'):
        path = as_utf8(path)
        output = self.execute_get_output(
            ['sh', '-c', 'for i in %s*; do printf "%%s\\0" "$i"; done' % shell_quote(path)],
            cwd=cwd)
        output = output.rstrip('\0')
        return output.split('\0')
