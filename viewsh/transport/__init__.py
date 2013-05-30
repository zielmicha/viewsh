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
    def file_completions(self, path, cwd='/', dirs_only=False):
        path = as_utf8(path)
        if dirs_only:
            cmd = '''for i in %s*; do
            if [ -d "$i" ]; then printf "%%s\\0" "$i"; fi
            done''' % shell_quote(path)
        else:
            cmd = 'for i in %s*; do printf "%%s\\0" "$i"; done' % shell_quote(path)
        output = self.execute_get_output(
            ['sh', '-c', cmd],
            cwd=cwd)
        output = output.rstrip('\0')
        return output.split('\0') if output else []
