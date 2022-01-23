#!/usr/bin/python
from symtable import Symbol

import AST


class RangeType(Symbol):
    def __init__(self, start, end):
        self.left = start
        self.right = end

    def __str__(self):
        return 'range'

class VariableSymbol(Symbol):

    def __init__(self, name, type):
        self.name = name
        self.type = type

class VectorSymbol(Symbol):

    def __init__(self, size, type):
        self.size = size
        self.type = type

    def __str__(self):
        return 'vector'

class SymbolTable(object):

    def __init__(self, parent, name): # parent scope and symbol table name
        self.parent = parent
        self.name = name
        self.variables = {}
    #

    def put(self, name, symbol): # put variable symbol or fundef under <name> entry
        self.variables[name] = symbol
    #

    def get(self, name): # get variable symbol or fundef from <name> entry
        if isinstance(name, AST.ID):
            name = name.id
        if self.variables.get(name) is not None:
            return self.variables.get(name)
        elif self.getParentScope() is not None:
            return self.getParentScope().get(name)
        else:
            return None
    #

    def getParentScope(self):
        return self.parent
    #

    def pushScope(self, name):
        return SymbolTable(self, name)
    #

    def popScope(self):
        return self.getParentScope()
    #

