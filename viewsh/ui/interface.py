
class Interface(object):
    def __init__(self):
        pass

    def log(self, *args):
        print ' '.join(map(str, args))
