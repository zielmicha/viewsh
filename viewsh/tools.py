from __future__ import print_function

def log(*args, **kwargs):
    _log_real(*map(str, args), **kwargs)

def _log_real(*args, **kwargs):
    # don't clobber terminal output
    pass # print('LOG', *args)

class Exit(BaseException):
    pass
