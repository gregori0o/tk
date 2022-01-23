import AST

def addToClass (cls):
  def decorator (func):
    setattr(cls, func.__name__, func)
    return func
  return decorator


class TreePrinter:

  @addToClass(AST.Program)
  def printTree(self, indent=0):
    self.program.printTree(indent)

  @addToClass(AST.Instructions)
  def printTree(self, indent):
    for instr in self.instructions:
      instr.printTree(indent)

  @addToClass(AST.IF_statement)
  def printTree(self, indent):
    print (("|  "*indent) + "IF")
    self.condition.printTree(indent+1)
    print (("|  "*indent) + "THEN")
    self.instr.printTree(indent+1)
    if self.else_instr is not None: 
      print (("|  "*indent) + "ELSE")
      self.else_instr.printTree(indent+1)

  @addToClass(AST.FOR_loop)
  def printTree(self, indent):
    print (("|  "*indent) + "FOR")
    print (("|  "*(indent+1)) + self.idx)
    print (("|  "*(indent+1)) + "RANGE")
    self.start.printTree(indent+2)#
    self.end.printTree(indent+2)#
    self.instr.printTree(indent+1)
  
  @addToClass(AST.WHILE_loop)
  def printTree(self, indent):
    print (("|  "*indent) + "WHILE")
    self.condition.printTree(indent+1)#
    self.instr.printTree(indent+1)

  @addToClass(AST.Assign)  
  def printTree(self, indent):
    print (("|  "*indent) + self.op)
    self.left.printTree(indent+1)
    self.right.printTree(indent+1)

  @addToClass(AST.Print)
  def printTree(self, indent):
    print (("|  "*indent) + "PRINT")
    self.to_print.printTree(indent+1)

  @addToClass(AST.Return)
  def printTree(self, indent):
    print (("|  "*indent) + "RETURN")
    self.to_return.printTree(indent+1)

  @addToClass(AST.Break)
  def printTree(self, indent):
    print (("|  "*indent) + "BREAK")

  @addToClass(AST.Continue)
  def printTree(self, indent):
    print (("|  "*indent) + "CONTINUE")

  @addToClass(AST.BinaryExpression)
  def printTree(self, indent):
    print(("|  "*indent) + self.operator)
    self.left.printTree(indent+1)
    self.right.printTree(indent+1)

  @addToClass(AST.Condition)
  def printTree(self, indent):
    print(("|  "*indent) + self.operator)
    self.left.printTree(indent+1)
    self.right.printTree(indent+1)

  @addToClass(AST.UnaryMinus)
  def printTree(self, indent):
    print(("|  "*indent) + "UMINUS")
    self.expr.printTree(indent+1)

  @addToClass(AST.Transposition)
  def printTree(self, indent):
    print(("|  "*indent) + "TRANSPOSE")
    self.expr.printTree(indent+1)

  @addToClass(AST.MatrixFromFunction)
  def printTree(self, indent):
    print(("|  "*indent) + self.function)
    print(("|  "*(indent+1)) + str(self.type))

  @addToClass(AST.ID)
  def printTree(self, indent):
    print(("|  "*indent) + self.id)

  @addToClass(AST.Number)
  def printTree(self, indent):
    print(("|  "*indent) + str(self.type)) 

  @addToClass(AST.List)
  def printTree(self, indent):
    if self.list is not None:
      self.list.printTree(indent)
    self.number.printTree(indent)

  @addToClass(AST.InnerList)
  def printTree(self, indent):
    print(("|  "*indent) + "VECTOR")
    self.list.printTree(indent+1)

  @addToClass(AST.OuterList)
  def printTree(self, indent):
    if self.outerlist is not None:
      self.outerlist.printTree(indent)
    self.innerlist.printTree(indent)

  @addToClass(AST.MatrixFromLists)
  def printTree(self, indent):
    print(("|  "*indent) + "VECTOR")
    self.outerlist.printTree(indent+1)


  @addToClass(AST.ToPrint)
  def printTree(self, indent): 
    if self.to_print is not None:
        self.to_print.printTree(indent)
    self.expr.printTree(indent)


  @addToClass(AST.Range)
  def printTree(self, indent):
    if self.right is not None:
      print(("|  "*indent) + "RANGE")
      self.left.printTree(indent+1)
      self.right.printTree(indent+1)
    else:
      self.left.printTree(indent)

