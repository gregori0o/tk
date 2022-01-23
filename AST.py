from dataclasses import dataclass


class Node(object):
	def accept(self, visitor):
		return visitor.visit(self)


@dataclass
class Program(Node):
	program: any


class Instructions(Node):
	def __init__(self, instr, list_instr=None):
		super().__init__()
		if list_instr is not None:
			self.instructions = list_instr.instructions
		else:
			self.instructions = []
		self.instructions.append(instr)


@dataclass
class IF_statement(Node):
	condition: any
	instr: any
	else_instr: any

@dataclass
class FOR_loop(Node):
	idx: any
	start: any
	end: any
	instr: any
	line: any


@dataclass
class WHILE_loop(Node):
	condition: any
	instr: any


@dataclass
class Assign(Node):
	left: any
	op: any
	right: any
	line: any


@dataclass
class Print(Node):
	to_print: any


@dataclass
class Return(Node):
	to_return: any

@dataclass
class Break(Node):
	line: any

@dataclass
class Continue(Node):
	line: any


@dataclass
class BinaryExpression(Node):
	left: any
	operator: any
	right: any
	line: any

@dataclass
class Condition(Node):
	left: any
	operator: any
	right: any

@dataclass
class UnaryMinus(Node):
	expr: any
	line: any


@dataclass
class Transposition(Node):
	expr: any


@dataclass
class MatrixFromFunction(Node):
	function: any
	type: any
	optional_type: any

@dataclass
class ID(Node):
	id: any

@dataclass
class Number(Node):
	type: any

@dataclass
class Str(Node):
	string: any

@dataclass
class List(Node):
	list: any
	number: any

@dataclass
class InnerList(Node):
	list: any

@dataclass
class OuterList(Node):
	outerlist: any
	innerlist: any
	line: any

@dataclass
class MatrixFromLists(Node):
	outerlist: any

@dataclass
class ToPrint(Node):
	to_print: any
	expr: any

@dataclass
class Range(Node):
	left: any
	right: any

@dataclass
class VectorElement(Node):
	id: any
	index: any
	line: any
	is_left_var: any

@dataclass
class MatrixElement(Node):
	id: any
	index_x: any
	index_y: any
	line: any
	is_left_var: any


