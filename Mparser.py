#!/usr/bin/python

import scanner
import ply.yacc as yacc
import AST

tokens = scanner.tokens

precedence = (
    ("nonassoc", 'IFX'),
    ("nonassoc", 'ELSE'),
    ("right", 'PLUSASSIGN', 'MINUSASSIGN', 'MULASSIGN', 'DIVASSIGN'),
    ("nonassoc", '<', '>', 'LESSEQ', 'GREATEREQ', 'NOTEQUAL', 'EQUAL'),
    ("left", '+', '-', 'DOTPLUS', 'DOTMINUS'),
    ("left", '/', '*', 'DOTDIV', 'DOTMUL'),
    ("right", 'UNARYMINUS'),
    ("left", "'"),
)


def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken('{1}', '{2}')".format(p.lineno, p.type, p.value))
    else:
        print("Unexpected end of input")


def p_program(p):
    """program : instructions"""
    p[0] = AST.Program(p[1])


def p_instructions(p):
    """instructions : instructions instruction
      | instruction"""
    if len(p) == 2:
        p[0] = AST.Instructions(p[1])
    else:
        p[0] = AST.Instructions(p[2], p[1])


def p_instruction(p):
    """instruction : '{' instructions '}'"""
    p[0] = p[2]


def p_expression(p):
    """expression : number
                  | matrix
                  | str
                  | innerlist
                  | left_var
                  | '(' expression ')'"""
    if len(p) > 3:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_string(p):
    """str : STRING"""
    p[0] = AST.Str(p[1])


def p_expression_binoperator(p):
    """expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression"""
    p[0] = AST.BinaryExpression(p[1], p[2], p[3], p.lineno(2))


def p_expression_dotoperator(p):
    """expression : expression DOTPLUS expression
                  | expression DOTMINUS expression
                  | expression DOTMUL expression
                  | expression DOTDIV expression"""
    p[0] = AST.BinaryExpression(p[1], p[2], p[3], p.lineno(2))


def p_condition(p):
    """condition : expression '>' expression
                 | expression '<' expression
                 | expression GREATEREQ expression
                 | expression LESSEQ expression
                 | expression EQUAL expression
                 | expression NOTEQUAL expression"""
    p[0] = AST.Condition(p[1], p[2], p[3])


def p_unaryminus(p):
    """expression : '-' expression %prec UNARYMINUS"""
    p[0] = AST.UnaryMinus(p[2], p.lineno(1))


def p_transpose(p):
    """expression : expression "'" """
    p[0] = AST.Transposition(p[1])


def p_instruction_if_else(p):
    """instruction : IF '(' condition ')' instruction %prec IFX
                   | IF '(' condition ')' instruction  ELSE instruction"""
    if len(p) == 6:
        p[0] = AST.IF_statement(p[3], p[5], None)
    else:
        p[0] = AST.IF_statement(p[3], p[5], p[7])


def p_instruction_for_loop(p):
    """instruction : FOR ID '=' expression ':' expression instruction"""
    p[0] = AST.FOR_loop(p[2], p[4], p[6], p[7], p.lineno(1))


def p_instruction_while_loop(p):
    """instruction : WHILE '(' condition ')' instruction"""
    p[0] = AST.WHILE_loop(p[3], p[5])


def p_matrix_from_func(p):
    """matrix : EYE '(' INT ')'
    	      | ZEROS '(' INT ')'
              | ONES '(' INT ')'
              | ZEROS '(' INT ',' INT ')'
              | ONES '(' INT ',' INT ')' """
    if len(p) == 5:
        p[0] = AST.MatrixFromFunction(p[1], p[3], p[3])
    elif len(p) == 7:
        p[0] = AST.MatrixFromFunction(p[1], p[3], p[5])


def p_matrix_from_lists(p):
    """matrix : '[' outerlist ']' """
    p[0] = AST.MatrixFromLists(p[2])


def p_outerlist(p):
    """outerlist : outerlist ',' innerlist
                 | innerlist"""
    if len(p) == 4:
        p[0] = AST.OuterList(p[1], p[3], p.lineno(2))
    elif len(p) == 2:
        p[0] = AST.OuterList(None, p[1], p.lineno(1))


def p_innerlist(p):
    """innerlist : '[' list ']'"""
    p[0] = AST.InnerList(p[2])


def p_list(p):
    """list : list ',' number
            | number"""
    if len(p) == 4:
        p[0] = AST.List(p[1], p[3])
    elif len(p) == 2:
        p[0] = AST.List(None, p[1])


def p_number(p):
    """number : INT
      | FLOAT"""
    p[0] = AST.Number(p[1])


def p_range(p):
    """range : INT ':' INT
      | INT"""
    if len(p) == 4:
        p[0] = AST.Range(p[1], p[3])
    elif len(p) == 2:
        p[0] = AST.Range(p[1], None)


# def p_ID(p):
#     """expression : ID"""
#     p[0] = p[1]

def p_var(p):
    """var : ID """
    p[0] = AST.ID(p[1])


def p_vector_element(p):
    """ vector_element : var "[" range "]"
    """
    p[0] = AST.VectorElement(p[1], p[3], p.lineno(2), False)


def p_matrix_element(p):
    """ matrix_element : var "[" range "," range "]" """
    p[0] = AST.MatrixElement(p[1], p[3], p[5], p.lineno(2), False)


def p_leftvar(p):
    """left_var : var
                | vector_element
                | matrix_element"""
    p[0] = p[1]


def p_assignmentID(p):
    """instruction : left_var '=' expression ';'
      | left_var PLUSASSIGN expression ';'
      | left_var MINUSASSIGN expression ';'
      | left_var MULASSIGN expression ';'
      | left_var DIVASSIGN expression ';'"""
    p[0] = AST.Assign(p[1], p[2], p[3], p.lineno(2))


# def p_keyword(p):
#     """instruction : CONTINUE ';'
#       | BREAK ';'
#       | RETURN expression ';'
#       | PRINT to_print ';'"""
#     if p[1] == 'print':
#       p[0] = AST.Print (p[2])
#     elif p[1] == 'return':
#       p[0] = AST.Return (p[2])
#     elif p[1] == 'break':
#       p[0] = AST.Break ()
#     elif p[1] == 'continue':
#       p[0] = AST.Continue ()

def p_print(p):
    """instruction : PRINT to_print ';'"""
    p[0] = AST.Print(p[2])


def p_return(p):
    """instruction : RETURN expression ';'"""
    p[0] = AST.Return(p[2])


def p_break(p):
    """instruction : BREAK ';'"""
    p[0] = AST.Break(p.lineno(1))


def p_continue(p):
    """instruction : CONTINUE ';'"""
    p[0] = AST.Continue(p.lineno(1))


def p_to_print(p):
    """to_print : to_print ',' expression
      | expression"""
    if len(p) == 4:
        p[0] = AST.ToPrint(p[1], p[3])
    else:
        p[0] = AST.ToPrint(None, p[1])


parser = yacc.yacc()
lexer = scanner.lexer
