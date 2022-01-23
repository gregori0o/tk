import sys
import ply.yacc as yacc
import Mparser
from TreePrinter import TreePrinter
from TypeChecker import TypeChecker
from Interpreter import Interpreter
from visit import *

if __name__ == '__main__':

    try:
        path = './examples/'
        filename = sys.argv[1] if len(sys.argv) > 1 else "matrix.m"
        filename = path + filename
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = Mparser.parser
    text = file.read()

    ast = parser.parse(text, lexer=Mparser.lexer)

    if ast is not None:
        # Below code shows how to use visitor
        typeChecker = TypeChecker()
        typeChecker.visit(ast)  # or alternatively ast.accept(typeChecker)
        if len(typeChecker.errors) == 0:
            ast.accept(Interpreter())
        else:
            print('\nType errors. Failed to start Interpreting.')
    else:
        print('\nSyntax errors. Failed to generate abstract syntax tree.')



    # in future
    # ast.accept(OptimizationPass1())
    # ast.accept(OptimizationPass2())
    # ast.accept(CodeGenerator())
