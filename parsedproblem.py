import math
#from numpy.dual import solve
from pyparsing import ParseException

from constraints import EqualityConstraint
from equationsolver import Problem, Context
from pyparsing import Word, alphas, nums, Literal, CaselessLiteral, Optional, Combine, ZeroOrMore, Group, Forward, \
    ParseResults, restOfLine, CaselessKeyword, Or, printables, QuotedString, Keyword, alphanums
from expressions import FixedValue, ProductExpression, SumExpression, PowerExpression, ScalarVariable, \
    DifferenceExpression, QuotientExpression, TanExpression, CosExpression, SinExpression, Constant
import six
import os
import inspect
__author__ = 'David Wyatt'

# An attempt to use pyparsing to parse a problem out of a text file


#testfilename = "examples/test.prob"
testfilename = "examples/test2.prob"
#testfilename = "C:/Users/David/Desktop/wrong.prob"
# Parser definition
# From http://eikke.com/pyparsing-introduction-bnf-to-code/6/index.html
# And pyparsing's fourfn

# Various elementary token definitions
point = Literal(".")
e = CaselessLiteral("E")
lPar = Literal('(').suppress()
rPar = Literal(')').suppress()
quot = Literal('\"').suppress()
equals = Literal('=').suppress()
assign = Literal(':=').suppress()
constassign = Literal('==').suppress()
signedDigitString = Word("+-" + nums, nums)
fNumber = Combine(signedDigitString + Optional(point + Optional(Word(nums))) + Optional(e + signedDigitString))
varName = Word(alphas+"_", alphanums+"_")
equationName = QuotedString(quoteChar="\"")
# What word to use to include another file's contents?
# http://en.wikipedia.org/wiki/Comparison_of_programming_languages_%28syntax%29#Libraries
# Python: import
# OpenSCAD: include (also use, but that's slightly different)
# C etc: #include
# LaTeX: \input, \include
# Java: import
# Modelica: import
# OK, let's go for import then...
importkeyword = Keyword("import").suppress()

# Constants
constantMap = {
  "pi": Constant("pi", math.pi),
  "e": Constant("e", math.e)
}
constant = Or([CaselessKeyword(constantName) for constantName in constantMap])
constant.setParseAction(lambda s, l, t: [constantMap[t[0]]])

# Parse numbers into floats straight away
fNumber.setParseAction(lambda s, l, t: [float(t[0])])

# Binary operators
binaryOperator = Word('+-*/^', exact=1) # N.B. To-the-power-of is ^ in this grammar at the moment - TODO make it accept Python syntax **
# Define mapping from binary operator symbols to composite expression classes
binaryOperatorMap = {
    '+': SumExpression,
    '-': DifferenceExpression,
    '*': ProductExpression,
    '/': QuotientExpression,
    '^': PowerExpression
}
# Now make binary operators get turned into classes straight away
binaryOperator.setParseAction(lambda s, l, t: [binaryOperatorMap[t[0]]])

# Likewise for unary operators
unaryOperatorMap = {
    'sin': SinExpression,
    'cos': CosExpression,
    'tan': TanExpression
}
unaryOperator = Or([CaselessKeyword(funcname) for funcname in unaryOperatorMap])
unaryOperator.setParseAction(lambda s, l, t: [unaryOperatorMap[t[0]]])

# Comments
comment = '#' + restOfLine

# Now, main structure of expression-parser
expr = Forward()
# atom is a number, variable, parenthesised expression or unary operator
atom = constant | fNumber | Group(lPar + expr + rPar) | Group(unaryOperator + lPar + Group(expr) + rPar) | varName
# Expr is an atom plus a succession of binary operators and expressions
expr << atom + ZeroOrMore(binaryOperator + Group(expr))
# Constraint is two expressions separated by an equals, possibly with an equation name at the end
constraint = Group(expr) + equals + Group(expr) + Optional(equationName)
# Variable initialisation is a variable name with ":=" and an expression
varinit = varName + assign + Group(expr)
# Constant definition is like varinit but with a "=="
constantdef = varName + constassign + Group(expr)
# Import command is import(filename)
importfilename = QuotedString(quoteChar="\"")
importcommand = importkeyword + lPar + importfilename + rPar

# Master line parser - optional to allow for blank lines
lineParser = Optional(constraint("constraint") | varinit("varinit") | constantdef("constdef") | importcommand("importcommand"))
lineParser.ignore(comment)

class ParsedProblem(Problem):
    def __init__(self, filename):
        super(ParsedProblem, self).__init__("Problem from file: " + os.path.abspath(filename))
        #os.chdir(os.path.dirname(os.path.abspath(__file__)))
        #sname=inspect.getframeinfo(inspect.currentframe()).filename
        #spath=os.path.dirname(os.path.abspath(sname))
        #spath=inspect.getabsfile()
        #print("Changing path to ", spath)
        #os.chdir(spath)
        self.parse_file(filename, set())
        self.print()

    def parse_file(self, filename, previous_files):
        print("------------------------------------------")
        print("Parsing", filename)
        previous_files.add(filename)
        with open(filename, 'r') as file:
            i = 1
            for line in file.readlines():
                # print("Trying to parse:",line)
                try:
                    parsedLine = lineParser.parseString(line)
                except ParseException as x:
                    print("Parse error at line", str(i), ":", str(x))
                    print("Original line:", line)
                if parsedLine.constraint:
                    # Equality constraint definition
                    # Now we need to turn these into expressions...
                    lhs = self.parseExpr(parsedLine[0])
                    rhs = self.parseExpr(parsedLine[1])

                    if len(parsedLine) == 2:
                        constr = EqualityConstraint("Line " + str(i), lhs, rhs)
                    elif len(parsedLine) == 3:  # Assume length is only 3 if we have a constraint title
                        constr = EqualityConstraint(str(parsedLine[2]), lhs, rhs)

                    # print(constr)
                    self.addConstr(constr)
                elif parsedLine.varinit:
                    # Variable initialisation line
                    # Find the variable (or make one if it doesn't exist already)
                    var = self.findVar(parsedLine[0])
                    # Parse the expression on the RHS
                    value_expr = self.parseExpr(parsedLine[1])
                    # See if we can get the value from a None context!
                    testval = value_expr.getValue(None)
                    # If we didn't get a None value returned:
                    if testval:
                        # Set the default value of the variable, which will be copied into every context it's used in!
                        var.value = testval
                    else:
                        print("Error in variable initialisation on line: ", str(i), parsedLine)
                    # Regardless, add the variable to the problem (in case it's new)
                    self.addExpression(var)
                elif parsedLine.constdef:
                    # TODO Constant initialisation line
                    constant_name = parsedLine[0]
                    # Parse the expression on the RHS
                    value_expr = self.parseExpr(parsedLine[1])
                    # See if we can get the value from a None context!
                    testval = value_expr.getValue(None)
                    # If we didn't get a None value returned:
                    if testval:
                        # Create a constant accordingly
                        constant = Constant(constant_name, testval)
                        # Add the constant to the problem
                        self.addExpression(constant)
                    else:
                        print("Error in constant definition on line: ", str(i), parsedLine)
                elif parsedLine.importcommand:
                    # Import command - parse another text file at this point!
                    subfilename = parsedLine[0]
                    # Turn it into a full path
                    subfilepath = os.path.join(os.path.dirname(filename), subfilename)
                    # Check this is a sane file name first!
                    if os.path.isfile(subfilepath):
                        # prevent infinite loops from mutual inclusion...
                        if subfilepath not in previous_files:
                            self.parse_file(subfilepath, previous_files)
                            # Although this is recursive I think the pass-by-reference of previous files will cover multiple consecutive calls...
                        else:
                            print("Error! Tried to re-import file", subfilepath, " at line ",str(i))
                    else:
                        print("Error! Could not import file", subfilepath, " at line ",str(i))
                 
                    

                # Finally increment line counter
                i += 1

    # Find the variable matching a string of its name
    def findVar(self, varName):
        matchVars = [var for var in self.exprs if var.name == varName]
        if len(matchVars) == 1:
            # Found a unique matching variable!
            return matchVars[0]
        elif len(matchVars) == 0:
            # No variable yet, need to make one
            newVar = ScalarVariable(varName)
            #print("Made a new variable: " + str(newVar))
            return newVar
        else:
            print("Error - multiple matching expressions for name: " + varName)
            print("Current exprs: " + self.exprs)
            return None

    def parseExpr(self, exprS):
        #print("Parsing", exprS)
        # Roots of recursion:
        # If it's a number, return a FixedValue
        if isinstance(exprS, float):
            return FixedValue(exprS)
        # If it's a constant, just return that
        elif isinstance(exprS, Constant):
            return exprS
        # If it's a string, return a variable of that name
        elif isinstance(exprS, six.string_types):
            # Attempt to obtain the corresponding variable if it exists already
            # Probably too clunky a way to do it...
            #print("Need to find/make ScalarVariable for: " + exprS)
            return self.findVar(exprS)
        elif isinstance(exprS, ParseResults):
            # It's another chunk of parsing!
            # Now it depends on the length
            # Hopefully the length of this will be either 1 or 3
            # If it's 1 it's a variable or number
            # So just recurse
            if len(exprS) == 1:
                return self.parseExpr(exprS[0])
            # If it's 2 it's a unary expression
            elif len(exprS) == 2:
                op = self.parseExpr(exprS[1])
                return exprS[0](op)
            # If it's 3 it's a binary expression
            elif len(exprS) == 3:
                op1 = self.parseExpr(exprS[0])
                op2 = self.parseExpr(exprS[2])
                return exprS[1](op1, op2)
            else:
                # Should never get here!
                print("Error parsing multi-part expression:", exprS)
        else:
            # Or here!
            print("Error parsing expression:", exprS)

if __name__ == '__main__':
    p = ParsedProblem(testfilename)
    #print(p)
    p.print()
    solveContext = p.defaultContext.copy()
    p.solve(solveContext)
    p.print(solveContext)



