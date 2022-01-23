 #!/usr/bin/python
from collections import defaultdict

import AST
from SymbolTable import SymbolTable, VectorSymbol, VariableSymbol, RangeType

ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))


operators = {
    'comparison': ['==', '!=', '<', '>', '>=', '<='],
    'math_bin': ['+', '-', '/', '*', 'concatenate'],
    'assignment': ['=', '+=', '-=', '/=', '*='],
    'math_dot_bin': ['.+', '.-', './', '.*'],
    'string_operators': ['+', '*', '+=', '*=']
}

for bin_op in operators['comparison']:
    ttype[bin_op]['int']['int'] = 'int'
    ttype[bin_op]['int']['float'] = 'int'
    ttype[bin_op]['float']['int'] = 'int'
    ttype[bin_op]['float']['float'] = 'int'

for bin_op in operators['assignment']:
    ttype[bin_op]['int']['int'] = 'int'
    ttype[bin_op]['int']['float'] = 'float'
    ttype[bin_op]['float']['int'] = 'float'
    ttype[bin_op]['float']['float'] = 'float'

for bin_op in operators['math_bin']:
    ttype[bin_op]['int']['int'] = 'int'
    ttype[bin_op]['int']['float'] = 'float'
    ttype[bin_op]['float']['int'] = 'float'
    ttype[bin_op]['float']['float'] = 'float'
    ttype[bin_op]['vector']['int'] = 'vector'
    ttype[bin_op]['vector']['float'] = 'vector'


for bin_op in operators['assignment']:
    ttype[bin_op]['vector']['vector'] = 'vector'
    ttype[bin_op]['vector']['int'] = 'vector'
    ttype[bin_op]['vector']['float'] = 'vector'

for bin_op in operators['math_bin']:
    ttype[bin_op]['vector']['vector'] = 'vector'

for op in operators['math_dot_bin']:
    ttype[op]['vector']['vector'] = 'vector'
    ttype[op]['vector']['int'] = 'vector'
    ttype[op]['int']['vector'] = 'vector'
    ttype[op]['vector']['float'] = 'vector'
    ttype[op]['float']['vector'] = 'vector'


for op in operators['string_operators']:
    ttype[op]['string']['int'] = 'string'
ttype['+']['string']['string'] = 'string'
ttype['+=']['string']['string'] = 'string'

errors_dict = {
    'assigment' : "Error with type in assigment",
    'assigment vectors sizes' : "Wrong sizes of vectors in assigment!",
    'continue': "Continue without loop!",
    'break': "Break without loop!",
    'for': "Indexes must be INT!",
    'bin exp': "Error type in expression!",
    'vectors size bin exp': "Wrong sizes of vectors in expression!",
    'condition': "Invalid types in condition",
    'uminus': "Invalid type in unary minus",
    'transposition type': "Invalid type in transposition",
    'dimension in transpition': "Wrong dimension in transposition",
    'vector size': "Invalid vector size",
    'range type': "Invalid type(s) in range",
    'index type': "Invalid index type",
    'vector type': "Invalid vector type or vector's dimension",
    'vector size': "Invalid size of vector",
    'index range': "Index out of range",
    'matrix size': "Invalid size of matrix",
}



class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)


    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    # simpler version of generic_visit, not so general
    #def generic_visit(self, node):
    #    for child in node.children:
    #        self.visit(child)


class Error:
    def __init__(self, line_number, content):
        self.line_number = line_number
        self.content = content

    def __str__(self):
        return f'{errors_dict[self.content]}, line {self.line_number}'

class TypeChecker(NodeVisitor):
    def __init_visit__(self):
        self.symbol_table = SymbolTable(None, 'main')
        self.errors = []
        self.loop_checker = 0

    def print_errors(self):
        for error in self.errors:
            print (error)

    def add_error(self, line_number, content):
        self.errors.append(Error(line_number, content))

    def visit_Program(self, node):
        self.__init_visit__()
        self.visit(node.program)
        self.print_errors()

    def visit_Instructions(self, node):
        #self.symbol_table = self.symbol_table.pushScope('block')
        for instruction in node.instructions:
            self.visit(instruction)
        #self.symbol_table.popScope()

    def visit_Assign(self, node):
        op = node.op
        if op == '=':
            right_type = self.visit(node.right)
            left_type = self.symbol_table.get(node.left.id)
            if right_type is None:
                self.add_error(node.line, 'assigment')
                return None
            if left_type is None:
                self.symbol_table.put(node.left.id, right_type)
                return
            str_left_type = ttype[op][str(left_type)][str(right_type)]
            if str(left_type) != str(right_type) and str(left_type) != ttype[op][str(left_type)][str(right_type)]:
                self.add_error(node.line, 'assigment')
                return None
        else:
            left_type = self.visit(node.left)
            right_type = self.visit(node.right)
            type = ttype[op][str(left_type)][str(right_type)]
            if type is None:
                self.add_error(node.line, 'assigment')
                return None
            if type == "vector":
                if isinstance(left_type, VectorSymbol) and isinstance(right_type, VectorSymbol):
                    if left_type.size != right_type.size:
                        self.add_error(node.line, 'assigment vectors sizes')
                        return None

    def visit_Number(self, node):
        if isinstance(node.type, int):
            return 'int'
        if isinstance(node.type, float):
            return 'float'
        return None

    def visit_Str(self, node):
        return 'string'

    def visit_Continue(self, node):
        if not self.loop_checker:
            self.errors.append(Error(node.line, 'continue'))

    def visit_Break(self, node):
        if not self.loop_checker:
            self.errors.append(Error(node.line, 'break'))

    def visit_Return(self, node):
        return self.visit(node.to_return)

    def visit_ID(self, node):
        return self.symbol_table.get(node.id)

    def visit_IF_statement(self, node):
        self.visit(node.condition)
        self.symbol_table = self.symbol_table.pushScope('if')
        self.visit(node.instr)
        if node.else_instr is not None:
            self.symbol_table.pushScope('else')
            self.visit(node.instr)
        self.symbol_table = self.symbol_table.popScope()

    def visit_FOR_loop(self, node):
        self.symbol_table = self.symbol_table.pushScope('for')
        self.symbol_table.put(node.idx, 'int')
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
        if start_type != 'int' or end_type != 'int':
            self.add_error(node.line, 'for')
        self.loop_checker +=1
        self.visit(node.instr)
        self.loop_checker -=1
        self.symbol_table = self.symbol_table.popScope()

    def visit_WHILE_loop(self, node):
        self.visit(node.condition)
        self.symbol_table = self.symbol_table.pushScope('while')
        self.loop_checker += 1
        self.visit(node.instr)
        self.loop_checker -= 1
        self.symbol_table = self.symbol_table.popScope()

    def visit_Print(self, node):
        self.visit(node.to_print)

    def visit_BinaryExpression(self, node):
        op = node.operator
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        type = ttype[op][str(left_type)][str(right_type)]

        ttst = str(right_type)

        if type is None:
            self.add_error(node.line, 'bin exp')
            return None
        if isinstance(left_type, VectorSymbol) and isinstance(right_type, VectorSymbol):
            if left_type.size != right_type.size:
                self.add_error(node.line, 'vectors size bin exp')
                return None
        if type == 'vector':
            return left_type if isinstance(left_type, VectorSymbol) else right_type
        return type

    def visit_Range(self, node):
        left = node.left
        right = node.right
        #if right is None:
        #    if type_left != 'int':
        #        self.add_error(node.line, 'range type')
        #        return None
        #    return RangeType()
        #type_right = self.visit(node.right_range)
        #if type_left != 'int' or type_right != 'int':
        #    self.add_error(node.line, 'range type')
        #    return None
        return RangeType(left, right)


    def visit_VectorElement(self, node):
        index = self.visit(node.index)
        if str(index) != 'range':
            self.add_error(node.line, 'index type')
            return None

        vector_type = self.symbol_table.get(node.id)
        if vector_type is None or not isinstance(vector_type, VectorSymbol):
            self.add_error(node.line, 'vector type')
            return None
        left, right = index.left, index.right
        if right is None:
            if not (0 <= left < vector_type.size[0]):
                self.add_error(node.line, 'index range')
                return None
            if len(vector_type.size) != 1:
                return VectorSymbol([vector_type.size[1]], vector_type.type)
            return vector_type.type

        if not (0 <= left < right <= vector_type.size[0]):
            self.add_error(node.line, 'index range')
            return None

        length = right-left
        if len(vector_type.size) != 1:
            return VectorSymbol([length, vector_type.size[1]], vector_type.type)
        return VectorSymbol([length], vector_type.type)

    def visit_MatrixElement(self, node):
        x, y = self.visit(node.index_x), self.visit(node.index_y)
        if str(x) != 'range' or str(y) != 'range':
            self.add_error(node.line, 'index type')
            return None

        matrix_type = self.visit(node.id)
        if matrix_type is None or not isinstance(matrix_type, VectorSymbol):
            self.add_error(node.line, 'vector type')
            return None

        if len(matrix_type.size) != 2:
            self.add_error(node.line, 'matrix size')
            return None

        x_left, x_right = x.left, x.right
        y_left, y_right = y.left, y.right
        max_x, max_y = matrix_type.size[0], matrix_type.size[1]
        if x_right is None and y_right is None:
            are_x_and_y_in_bounds = 0 <= x_left < max_x and 0 <= y_left < max_y
            if not are_x_and_y_in_bounds:
                self.add_error(node.line, 'index range')
                return None
            return matrix_type.type
        if x_right is None:
            are_x_and_y_in_bounds = 0 <= x_left < max_x and 0 <= y_left < y_right <= max_y
            if not are_x_and_y_in_bounds:
                self.add_error(node.line, 'index range')
                return None
            return VectorSymbol([y_right - y_left], matrix_type.type)
        if y_right is None:
            are_x_and_y_in_bounds = 0 <= x_left < x_right <= max_x and 0 <= y_left < max_y
            if not are_x_and_y_in_bounds:
                self.add_error(node.line, 'index range')
                return None
            return VectorSymbol([x_right - x_left], matrix_type.type)

        are_x_and_y_in_bounds = 0 <= x_left < x_right <= max_x and 0 <= y_left < y_right <= max_y
        if not are_x_and_y_in_bounds:
            self.add_error(node.line, 'index range')
            return None

        x_length = x_right - x_left
        y_length = y_right - y_left

        return VectorSymbol([x_length, y_length], matrix_type.type)

    def visit_Condition(self, node):
        type_left = self.visit(node.left)
        type_right = self.visit(node.right)
        op = node.operator
        ttype_ = ttype[op][str(type_left)][str(type_right)]
        if ttype_ is not None:
            return ttype_
        else:
            self.add_error(node.line, 'condition')
            return None

    def visit_UnaryMinus(self, node):
        exp_type = self.visit(node.expr)
        if not str(exp_type) in ['int', 'vector', 'float']:
            self.add_error(node.line, 'uminus')
            return None

        return exp_type

    def visit_Transposition(self, node):
        vector_type = self.visit(node.expr)
        if not isinstance(vector_type, VectorSymbol):
            self.add_error(node.line, 'transposition type')

        if len(vector_type.size) == 1:
            return VectorSymbol([1, vector_type.size], vector_type.type)
        elif len(vector_type.size) == 2:
            return VectorSymbol(reversed(vector_type.size), vector_type.type)
        else:
            self.add_error(node.line, 'dimension in transpition')
            return None

    def visit_MatrixFromFunction(self, node):
        if node.optional_type is None:
            return VectorSymbol((node.type, node.type), 'int')
        return VectorSymbol((node.type, node.optional_type), 'int')

    def visit_List(self, node):
        type = self.visit(node.number)
        if node.list is None:
            return VectorSymbol([1], type)
        old_list = self.visit(node.list)
        type = ttype['concatenate'][type][old_list.type]
        return VectorSymbol([1+old_list.size[0]], type)

    def visit_InnerList(self, node):
        return self.visit(node.list)

    def visit_OuterList(self, node):
        innerlist = self.visit(node.innerlist)
        if node.outerlist is None:
            return VectorSymbol([innerlist.size[0], 1], innerlist.type)
        old_list = self.visit(node.outerlist)
        if old_list is None:
            return None
        old_size = old_list.size[0]
        if old_size != innerlist.size[0]:
            self.add_error(node.line, 'vector size')
            return None
        type = ttype['concatenate'][innerlist.type][old_list.type]
        return VectorSymbol([old_size, 1+old_list.size[1]], type)

    def visit_MatrixFromLists(self, node):
        return self.visit(node.outerlist)

    def visit_ToPrint(self, node):
        self.visit(node.expr)
        if node.to_print is not None:
            self.visit(node.to_print)

