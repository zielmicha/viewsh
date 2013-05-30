from __future__ import print_function
import re

def log(*args, **kwargs):
    _log_real(*map(str, args), **kwargs)

def _log_real(*args, **kwargs):
    # don't clobber terminal output
    pass # print('LOG', *args)

class Exit(BaseException):
    pass

import re
_quote_pos = re.compile('(?=[^-0-9a-zA-Z_./\n])')

def shell_quote(arg):
    if arg:
        return _quote_pos.sub('\\\\', arg).replace('\n',"'\n'")
    else:
        return "''"

def as_utf8(arg):
    if isinstance(arg, str):
        return arg
    else:
        return arg.encode('utf8')
