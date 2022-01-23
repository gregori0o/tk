
import AST
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys
import numpy as np

sys.setrecursionlimit(10000)

memory_stack = MemoryStack(Memory('global'))

binary_operators = {
    '+': lambda x, y: x+y,
    '-': lambda x, y: x-y,
    '/': lambda x, y: x / y,
    '*': lambda x, y: x*y, #if isinstance(y, int) else np.dot(x, y),

    '.+': lambda x, y: x+y,
    '.-': lambda x, y: x-y,
    '.*': lambda x, y: x*y,
    './': lambda x, y: x/y,

    '>': lambda x, y: x > y,
    '<': lambda x, y: x < y,
    '>=': lambda x, y: x >= y,
    '<=': lambda x, y: x <= y,
    '==': lambda x, y: x == y,
    '!=': lambda x, y: x != y,
}

unary_operators = {
    '-': lambda x: -x,
    'T': lambda x: x.T
}

matrix_functions = {
    'zeros': lambda x, y: np.zeros((x, y)),
    'ones': lambda x, y: np.ones((x, y)),
    'eye': lambda x: np.eye(x)
}



class Interpreter(object):


    @on('node')
    def visit(self, node):
        pass

    @when(AST.Program)
    def visit(self, node):
        node.program.accept(self)

    @when(AST.Instructions)
    def visit(self, node):
        for instruction in node.instructions:
            instruction.accept(self)

    @when(AST.IF_statement)
    def visit(self, node):
        if node.condition.accept(self):
            node.instr.accept(self)
        elif node.else_instr is not None:
            node.else_instr.accept(self)

    @when(AST.FOR_loop)
    def visit(self, node):
        memory_stack.push(Memory("for"))

        for i in range (node.start.accept(self), node.end.accept(self)):
            memory_stack.set(node.idx, i)
            try:
                node.instr.accept(self)
            except BreakException:
                break
            except ContinueException:
                continue

        memory_stack.pop()

    @when(AST.WHILE_loop)
    def visit(self, node):
        memory_stack.push(Memory("while"))

        while node.condition.accept(self):
            try:
                node.instr.accept(self)
            except BreakException:
                break
            except ContinueException:
                continue

        memory_stack.pop()

    @when(AST.Assign)
    def visit(self, node):
        right = node.right.accept(self)

        if node.op == '=':
            if isinstance(node.left, AST.VectorElement):
                node.left.is_left_var = True
                vector = node.left.accept(self)
                vector[:] = right
                node.left.is_left_var = False
            elif isinstance(node.left, AST.MatrixElement):
                node.left.is_left_var = True
                matrix = node.left.accept(self)
                matrix[:] = right
                node.left.is_left_var = False
            else:
                if isinstance(right, list):
                    right = np.array(right)
                memory_stack.set(node.left.id, right)
        else:
            if isinstance(node.left, AST.VectorElement):
                node.left.is_left_var = True
                vector = node.left.accept(self)
                vector[:] = binary_operators[node.op[0]](vector, right)
                node.left.is_left_var = False
            elif isinstance(node.left, AST.MatrixElement):
                node.left.is_left_var = True
                matrix = node.left.accept(self)
                matrix[:] = binary_operators[node.op[0]](matrix, right)
                node.left.is_left_var = False
            else:
                left = node.left.accept(self)
                value = binary_operators[node.op[0]](left, right)
                memory_stack.set(node.left.id, value)

    @when(AST.Print)
    def visit(self, node):
        node.to_print.accept(self)
        print("")

    @when(AST.ToPrint)
    def visit(self, node):
        if node.to_print is not None:
            node.to_print.accept(self)
        print(node.expr.accept(self), end=" ")

    @when(AST.Return)
    def visit(self, node):
        print(node.to_return.accept(self))
        sys.exit()

    @when(AST.Break)
    def visit(self, node):
        raise BreakException

    @when(AST.Continue)
    def visit(self, node):
        raise ContinueException

    @when(AST.BinaryExpression)
    def visit(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        return binary_operators[node.operator](left, right)

    @when(AST.Condition)
    def visit(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        return binary_operators[node.operator](left, right)

    @when(AST.UnaryMinus)
    def visit(self, node):
        value = node.expr.accept(self)

        return (-1) * value

    @when(AST.Transposition)
    def visit(self, node):
        value = node.expr.accept(self)

        return value.T

    @when(AST.MatrixFromFunction)
    def visit(self, node):
        if node.function == 'eye':
            return matrix_functions[node.function](node.type)
        return matrix_functions[node.function](node.type, node.optional_type)

    @when(AST.ID)
    def visit(self, node):
        return memory_stack.get(node.id)

    @when(AST.Number)
    def visit(self, node):
        return node.type

    @when(AST.Str)
    def visit(self, node):
        return node.string

    @when(AST.MatrixFromLists)
    def visit(self, node):
        return node.outerlist.accept(self)

    @when(AST.OuterList)
    def visit(self, node):
        inner = node.innerlist.accept(self)
        if node.outerlist is None:
            return [inner]
        outer = node.outerlist.accept(self)
        return outer.append(inner)

    @when(AST.InnerList)
    def visit(self, node):
        return node.list.accept(self)

    @when(AST.List)
    def visit(self, node):
        num = node.number.accept(self)
        if node.list is None:
            return [num]
        list = node.list.accept(self)
        return list.append(num)

    @when(AST.Range)
    def visit(self, node):
        """
        left = node.left if isinstance(node.left, int) else node.left.accept(self)
        right = node.right if isinstance(node.right, int) else node.right.accept(self)
        return left, right
        """
        return node.left, node.right

    @when(AST.VectorElement)
    def visit(self, node):
        index = node.index.accept(self)
        vector = memory_stack.get(node.id.id)

        if isinstance(index[0], int) and isinstance(index[1], int):
            return vector[int(index[0]):int(index[1])]
        elif node.is_left_var and isinstance(index[0], int) and index[1] is None:
            return vector[int(index[0]):int(index[0]+1)]
        elif isinstance(index[0], int):
            return vector[int(index[0])]
        else:
            raise RuntimeError(f"{node.line}: Invalid indices type!")

    @when(AST.MatrixElement)
    def visit(self, node):
        index_x, index_y = node.index_x.accept(self), node.index_y.accept(self)
        matrix = memory_stack.get(node.id.id)

        if isinstance(index_x[0], int) and isinstance(index_x[1], int) and\
           isinstance(index_y[0], int) and isinstance(index_y[1], int):
            return matrix[int(index_x[0]):int(index_x[1]), int(index_y[0]):int(index_y[1])]
        elif node.is_left_var and isinstance(index_x[0], int) and index_x[1] is None and isinstance(index_y[0], int) and index_y[1] is None:
            return matrix[int(index_x[0]):int(index_x[0]+1), int(index_y[0]):int(index_y[0]+1)]
        elif node.is_left_var and isinstance(index_x[0], int) and isinstance(index_x[1], int) and  \
                isinstance(index_y[0], int) and index_y[1] is None:
            return matrix[int(index_x[0]):int(index_x[1]), int(index_y[0]):int(index_y[0])+1]
        elif node.is_left_var and isinstance(index_x[0], int) and index_x[1] is None and  \
                isinstance(index_y[0], int) and isinstance(index_y[1], int):
            return matrix[int(index_x[0]):int(index_x[0])+1, int(index_y[0]):int(index_y[1])]
        elif isinstance(index_x[0], int) and index_x[1] is None and isinstance(index_y[0], int) and index_y[1] is None:
            return matrix[int(index_x[0]), int(index_y[0])]
        elif isinstance(index_x[0], int) and isinstance(index_x[1], int) and  \
                isinstance(index_y[0], int) and index_y[1] is None:
            return matrix[int(index_x[0]):int(index_x[1]), int(index_y[0])]
        elif isinstance(index_x[0], int) and index_x is None and  \
                isinstance(index_y[0], int) and isinstance(index_y[1], int):
            return matrix[int(index_x[0]), int(index_y[0]):int(index_y[1])]
        else:
            raise RuntimeError(f"{node.line}: Invalid indices type!")
