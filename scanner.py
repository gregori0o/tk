import ply.lex as lex

literals = "=+-*/',;:()[]{}"

reserved = {
    'if'    : 'IF',
    'else'  : 'ELSE',
    'for'   : 'FOR',
    'while' : 'WHILE',
    'break' : 'BREAK',
    'continue' : 'CONTINUE',
    'return' : 'RETURN',
    'eye' : 'EYE',
    'zeros' : 'ZEROS',
    'ones' : 'ONES',
    'print' : 'PRINT'
}

tokens = ['ID', 'FLOAT', 'INT', 'STRING', 'DOTPLUS', 'DOTMINUS', 'DOTMUL', 'DOTDIV', 'LESSEQ', 'GREATEREQ', 'NOTEQUAL', 'EQUAL', 'PLUSASSIGN', 'MINUSASSIGN', 'MULASSIGN', 'DIVASSIGN'] + list(reserved.values())


t_ignore = ' \t'


t_DOTPLUS = r'\.\+'
t_DOTMINUS = r'\.-'
t_DOTMUL = r'\.\*'
t_DOTDIV = r'\./'
t_LESSEQ = r'<='
t_GREATEREQ = r'>='
t_NOTEQUAL = r'!='
t_EQUAL = r'=='
t_PLUSASSIGN = r'\+='
t_MINUSASSIGN = r'-='
t_MULASSIGN = r'\*='
t_DIVASSIGN = r'/='


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t) :
    print ("Illegal character '%s'" %t.value[0])
    t.lexer.skip(1)

def t_comment(t):
    r'\#.*'
    pass

def t_ID(t):
    r'[a-zA-Z_][\w_]*'
    t.type = reserved.get(t.value,'ID')
    return t

def t_FLOAT(t):
    r'(\.\d+|\d+\.\d*)(E[+-]?\d+)?|\d+E[+-]?\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'".*"'
    t.value = str(t.value)[1:-1]
    return t

lexer = lex.lex()