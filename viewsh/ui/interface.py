from viewsh.ui import toolkit

class Interface(object):
    pass

class InterfaceWrapper(object):
    def __init__(self, iface):
        self.iface = iface

    def __getattr__(self, name):
        orig = getattr(self.iface, name)
        def wrapper(*args, **kwargs):
            return toolkit.run_in_ui(lambda: orig(*args, **kwargs))

        return wrapper
