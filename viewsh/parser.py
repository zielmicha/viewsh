from . import tools
import re

class Node(object):
    pass

class NodeWithChildren(Node):
    pass

class Backtick(NodeWithChildren):
    def __init__(self, child):
       self.child = child

    @property
    def children(self):
        return (self.child, )

    def __repr__(self):
        return '$( %r )' % self.child

class Pipeline(NodeWithChildren):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return ' | '.join( repr(child) for child in self.children)

class Identifier(Node):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return tools.shell_quote(self.text)

class Redirect(Node):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

class Compound(NodeWithChildren):
    def __init__(self, type, a, b):
        self.type = type
        self.a = a
        self.b = b

    @property
    def children(self):
        return (self.a, self.b)

    def __repr__(self):
        return '(%r %s %r)' % (self.a, self.type, self.b)

class Concat(NodeWithChildren):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return ''.join( repr(child) for child in self.children )

class Command(NodeWithChildren):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return ' '.join( repr(child) for child in self.children )

single_quoted = '([^\']|\'\\\'\')*'
identifier = re.compile('^([^|$()&<>"\'; ]*|\'' + single_quoted + '\')')
quoted_identifier = re.compile('^[^$\"]*')

def parse(text, strict=False):
    ast, rest = parse_with_remainder(text, strict=strict)
    return ast

def parse_with_remainder(text, strict=False):
    ast, text = parse_fragment(text, strict=strict)

    if text.startswith(('&&', '||')):
        type = text[:2]
        rest = text[2:]
    elif text.startswith(';'):
        type = text[:1]
        rest = text[1:]
    else:
        return ast, text

    next_ast, rest = parse_with_remainder(rest, strict=strict)
    return Compound(type, ast, next_ast), rest

def parse_fragment(text, strict):
    '''
    Parses viewsh shell syntax. Returns tuple (ast, remaining)
    Uses regex, but don't be afraid - it's just for tokenization.

    Supported syntax:
    | - pipe
    $(), `` - backtick
    () - parens
    &&, ||, ; - stops parsing
    "", '' - quote
    # - comment
    >, <, n> - redirection
    '''
    pipeline = []
    command = []
    quote_mode = False
    quote_mode_command_before = []

    def end_command():
        if command:
            pipeline.append(Command(list(command)))
            command[:] = []

    while text:
        if not quote_mode:
            text = text.lstrip()
        regex = (quoted_identifier if quote_mode else identifier)
        ident_match = regex.match(text).group(0)


        if not quote_mode and text.startswith(('>', '<')):
            command.append(Redirect(text[:1]))
            text = text[1:]
        elif not quote_mode and text[1:].startswith(('>', '<')):
            command.append(Redirect(text[:2]))
            text = text[2:]
        elif not quote_mode and text.startswith('#'):
            text = ''
        elif ident_match:
            command.append(Identifier(ident_match))
            text = text[len(ident_match):]
        elif text.startswith((';', '&&', '||')):
            break
        elif text.startswith(')'):
            text = text[1:]
            break
        elif text.startswith('$('):
            ast, text = parse_with_remainder(text[2:], strict=strict)
            command.append(Backtick(ast))
        elif text.startswith('('):
            ast, text = parse_with_remainder(text[2:], strict=strict)
            command.append(ast)
        elif text.startswith('|'):
            end_command()
            text = text[1:]
        elif text.startswith('"'):
            if quote_mode:
                quote_mode = False
                quote_mode_command_before.append(Concat(command))
                command = quote_mode_command_before
            else:
                quote_mode = True
                quote_mode_command_before = command
                command = []
            text = text[1:]
        else:
            if strict:
                raise ValueError('bad token %r' % tools.trim_long_string(text))
            else:
                text = text[1:]

    end_command()

    return Pipeline(pipeline), text

if __name__ == '__main__':
    print parse('a b')
    print parse('a b; c')
    print parse('a $(c d; e)')
    print parse('a && b')
    print parse('a | b')
    print parse('a "b $(v | g) c" d')
    print parse('a | b # c')
    print parse('a | b# c')
    print parse('a >b < c 3> d')

    import os
    parse(os.urandom(20000))
