
class Interface(object):
    def __init__(self, debug_level=0):
        self.debug_level = debug_level

    def log(self, *args, **kwargs):
        level = kwargs.get('level', 0)
        if level <= self.debug_level:
            print ' '.join(map(str, args))

    def quit(self):
        raise SystemExit

    def patch_log(self):
        # set local viewsh.log to remote function
        import viewsh.tools
        viewsh.tools._log_real = self.log
