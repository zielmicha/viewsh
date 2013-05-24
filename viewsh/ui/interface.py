
class Interface(object):
    def __init__(self, debug_level=0):
        self.debug_level = debug_level

    def log(self, *args, **kwargs):
        level = kwargs.get('level', 0)
        if level <= self.debug_level:
            print ' '.join(map(str, args))
