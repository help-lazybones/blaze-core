"""
The improved parser for Datashape grammar.

Grammar::

    top : mod
        | stmt

    mod : mod mod
        | stmt

    stmt : TYPE lhs_expression EQUALS rhs_expression
         | rhs_expression

    lhs_expression : lhs_expression lhs_expression
                   | NAME

    rhs_expression : rhs_expression COMMA rhs_expression
                   | appl
                   | record
                   | BIT
                   | NAME
                   | NUMBER

    appl : NAME '(' rhs_expression ')'

    record : LBRACE record_opt RBRACE
    record_opt : record_opt SEMI record_opt
               | record_item
               | empty
    record_item : NAME COLON '(' rhs_expression ')'
                | NAME COLON rhs_expression'

    empty :

"""

import os
import sys

from functools import partial
from collections import namedtuple
import coretypes as T

try:
    import dlex
    import dyacc
    DEBUG = False
except:
    DEBUG = True

from blaze.plyhacks import yaccfrom, lexfrom
from blaze.error import CustomSyntaxError

#------------------------------------------------------------------------
# Errors
#------------------------------------------------------------------------

class DatashapeSyntaxError(CustomSyntaxError):
    pass

#------------------------------------------------------------------------
# Lexer
#------------------------------------------------------------------------

tokens = (
    'TYPE', 'NAME', 'NUMBER', 'EQUALS', 'COMMA', 'COLON',
    'LBRACE', 'RBRACE', 'SEMI', 'BIT'
)

literals = [
    '=' ,
    ',' ,
    '(' ,
    ')' ,
    ':' ,
    '{' ,
    '}' ,
]

bits = set([
    'bool',
    'blob', # XXX deprecated
    'int',
    'float',
    'int8',
    'int16',
    'int32',
    'int64',
    'int64',
    'uint8',
    'uint16',
    'uint32',
    'uint64',
    'uint64',
    'uint64',
    'float16',
    'float32',
    'float64',
    'float128',
    'complex64',
    'complex128',
    'complex256',
    'object',
    'datetime64',
    'timedelta64',
])

t_EQUALS = r'='
t_COMMA  = r','
t_COLON  = r':'
t_SEMI   = r';'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_ignore = '[ ]'

def t_TYPE(t):
    r'type'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in bits:
        t.type = 'BIT'
    return t

def t_COMMENT(t):
    r'\#.*'
    pass

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print("Unknown token '%s'" % t.value[0])
    t.lexer.skip(1)

#------------------------------------------------------------------------
# Parser
#------------------------------------------------------------------------

precedence = (
    ('right' , 'COMMA'),
)

bittype     = namedtuple('bit', 'name')
tyinst     = namedtuple('tyinst', 'conargs')
tydecl     = namedtuple('tydecl', 'lhs, rhs')
tyappl     = namedtuple('tyappl', 'head, args')
tyrecord   = namedtuple('tyrecord', 'elts')
simpletype = namedtuple('simpletype', 'nargs, tycon, tyvars')

def p_top(p):
    '''top : mod
           | stmt
    '''
    p[0] = p[1]

#------------------------------------------------------------------------

def p_decl1(p):
    'mod : mod mod'
    p[0] = [p[1], p[2]]

def p_decl2(p):
    'mod : stmt'
    p[0] = p[1]

#------------------------------------------------------------------------

def p_statement_assign(p):
    'stmt : TYPE lhs_expression EQUALS rhs_expression'

    # alias
    if len(p[2]) == 1:
        constructid = p[2][0]
        parameters  = ()
        rhs         = p[4]

    # paramaterized
    else:
        constructid = p[2][0]
        parameters  = p[2][1:]
        rhs         = p[4]

    lhs = simpletype(len(parameters), constructid, parameters)
    p[0] = tydecl(lhs, rhs)

def p_statement_expr(p):
    'stmt : rhs_expression'
    p[0] = tyinst(p[1])

#------------------------------------------------------------------------

def p_lhs_expression(p):
    'lhs_expression : lhs_expression lhs_expression'
    # tuple addition
    p[0] = p[1] + p[2]

def p_lhs_expression_node(p):
    'lhs_expression : NAME'
    p[0] = (p[1],)

#------------------------------------------------------------------------

def p_rhs_expression_node1(p):
    '''rhs_expression : appl
                      | record'''
    p[0] = p[1]

def p_rhs_expression_node2(p):
    '''rhs_expression : BIT'''
    p[0] = (bittype(p[1]),)

def p_rhs_expression_node3(p):
    '''rhs_expression : NAME
                      | NUMBER'''
    p[0] = (p[1],)

def p_rhs_expression(p):
    'rhs_expression : rhs_expression COMMA rhs_expression'''
    # tuple addition
    p[0] = p[1] + p[3]

#------------------------------------------------------------------------

def p_appl(p):
    "appl : NAME '(' rhs_expression ')'"
    p[0] = (tyappl(p[1], p[3]),)

#------------------------------------------------------------------------

def p_record(p):
    'record : LBRACE record_opt RBRACE'
    p[0] = (tyrecord(p[2]),)

def p_record_opt1(p):
    'record_opt : record_opt SEMI record_opt'
    p[0] = p[1] + p[3]

def p_record_opt2(p):
    'record_opt : record_item'
    p[0] = [p[1]]

def p_record_opt3(p):
    'record_opt : empty'
    p[0] = []

def p_record_item1(p):
    "record_item : NAME COLON '(' rhs_expression ')' "
    p[0] = (p[1], p[4])

def p_record_item2(p):
    '''record_item : NAME COLON rhs_expression'''
    p[0] = (p[1], p[3])

#------------------------------------------------------------------------

def p_empty(t):
    'empty : '
    pass

def p_error(p):
    if p:
        raise DatashapeSyntaxError(
            p.lineno,
            p.lexpos,
            '<stdin>',
            p.lexer.lexdata,
        )
    else:
        print("Syntax error at EOF")

#------------------------------------------------------------------------
# Toplevel
#------------------------------------------------------------------------

reserved = {
    'Record'   : T.Record,
    'Range'    : T.Range,
    'Either'   : T.Either,
    'Varchar'  : T.Varchar,
    'Union'    : T.Union,
    'Option'   : T.Option,
    'string'   : T.String, # String type per proposal
}

python_internals = (int, long, basestring)

def build_ds_extern(ds):
    if isinstance(ds, list):
        return map(build_ds, ds)
    elif isinstance(ds, simpletype):
        pass # XXX
    elif isinstance(ds, tydecl):
        pass

def build_ds(ds):
    """
    Build a datashape instance from parse tree. In the case where we
    have a named instance disregard the naming and the parameters and
    return an anonymous type.
    """
    # ----------------------------
    if isinstance(ds, list):
        pass # XXX
    elif isinstance(ds, simpletype):
        pass # XXX
    elif isinstance(ds, tydecl):
        if isinstance(ds.lhs , simpletype):
            return build_ds(ds.rhs[0])
        else:
            raise NotImplementedError
    # ----------------------------

    elif isinstance(ds, tyinst):
        dst = map(build_ds, ds.conargs)
        return T.DataShape(dst)
    elif isinstance(ds, bittype):
        return T.Type._registry[ds.name]
    elif isinstance(ds, (int, long)):
        return T.Fixed(ds)
    elif isinstance(ds, basestring):
        return T.TypeVar(ds)
    elif isinstance(ds, tyappl):
        if ds.head in reserved:
            args = map(build_ds, ds.args)
            return reserved[ds.head](*args)
        else:
            raise NameError, ds.head
    elif isinstance(ds, tyrecord):
        # TODO: ugly hack
        return T.Record([(a, build_ds(b[0])) for a,b in ds.elts])
    else:
        raise ValueError, 'Invalid construction from Datashape parser: %s' % repr(ds)

def debug_parse(data, lexer, parser):
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok: break
        print tok
    return parser.parse(data)

def load_parser(debug=False):
    if debug:
        from ply import lex, yacc
        path = os.path.relpath(__file__)
        dir_path = os.path.dirname(path)
        lexer = lex.lex(lextab="dlex", outputdir=dir_path, optimize=1)
        parser = yacc.yacc(tabmodule='dyacc',outputdir=dir_path,
                write_tables=1, debug=0, optimize=1)
        return partial(debug_parse, lexer=lexer, parser=parser)
    else:
        module = sys.modules[__name__]
        lexer = lexfrom(module, dlex)
        parser = yaccfrom(module, dyacc, lexer)

        # curry the lexer into the parser
        return partial(parser.parse, lexer=lexer)

#------------------------------------------------------------------------
# Toplevel
#------------------------------------------------------------------------

def parse(pattern):
    parser = load_parser()
    res = parser(pattern)

    ds = build_ds(res)
    return ds

def parse_extern(pattern):
    parser = load_parser()
    res = parser(pattern)

    ds = build_ds_extern(res)
    return ds

if __name__ == '__main__':
    import readline
    parser = load_parser()
    readline.parse_and_bind('')

    while True:
        try:
            line = raw_input('>> ')
            ast = parser(line)
            print ast
            #print build_ds(ast)
        except EOFError:
            break
