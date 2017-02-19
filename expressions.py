from abc import abstractmethod
from abc import ABCMeta
from functools import total_ordering
import math

from NIbase import addDescVarOrRecurse

__author__ = 'David'

@total_ordering
class Expression(metaclass=ABCMeta):
    def __init__(self, name, childexprs=[]):
        self.name = name
        self.childExprs = childexprs

    def getName(self):
        return self.name

    def __eq__(self, other):
        return self.getName() == other.getName()

    def __lt__(self, other):
        return self.getName() < other.getName()

    def __hash__(self):
        return hash(self.getName())

    def getChildren(self):
        return self.childExprs

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def getValue(self, context):
        pass

    @abstractmethod
    def setValue(self, value, context):
        pass

    @abstractmethod
    def isComposite(self):
        pass

    @abstractmethod
    def getUndefinedExprs(self, context):
        pass

class Variable(Expression):
    def __init__(self, name, value):
        super(Variable, self).__init__(name)
        self.value = value

    def getValue(self, context):
        return self.value

    def isComposite(self):
        return False

    def getUndefinedExprs(self, context):
        return []

# A standard scalar variable
class ScalarVariable(Variable):
    def __init__(self, name, value=None):
        super(ScalarVariable, self).__init__(name, value)

    def __repr__(self):
        return "<ScalarVariable: name " + self.getName() + ", value " + str(self.value) + ">"

    def getValue(self, context):
        if context:
            return context.getValue(self) #self.value
        else:
            return None

    def setValue(self, value, context):
        #self.value = value
        context.setValue(self, value)

    def getUndefinedExprs(self, context):
        return [] if self.getValue(context) else [self]

    def copy(self):
        return ScalarVariable(name=self.name, value=self.value)

# A constant - something with a name and a fixed numerical value that cannot change
class Constant(Variable):
    def __repr__(self):
        return "<Constant: name " + self.name + ", value " + str(self.value) + ">"

    def setValue(self, value, context):
        #self.value = value
        pass
        # TODO Throw an error at this point?

# A slight shortcut for when you really need a hard-coded value!
class FixedValue(Variable):
    def __init__(self, value):
        super(FixedValue, self).__init__(str(value), value)

    def __repr__(self):
        return "<FixedValue: " + self.name + ">"

    def setValue(self, value, context):
        #self.value = value
        pass
        # TODO Throw an error at this point?

###################################################################################
# Composite expressions

class CompositeExpression(Expression):
    def __init__(self, name, childexprs=[]):
        super(CompositeExpression, self).__init__(name, childexprs)

    def isComposite(self):
        return True

    def getUndefinedExprs(self, context):
        exprlist = []
        for childexpr in self.getChildren():
            exprlist.extend(childexpr.getUndefinedExprs(context))
        return exprlist

###################################################################################
# Unary (1 argument)
class UnaryExpression(CompositeExpression):
    def __init__(self, arg):
        self.setArg(arg)
        super(UnaryExpression, self).__init__(self.getTextFormula(), [self.arg])

    def getTextFormula(self):
        return self.operatorTxt + "(" + self.arg.name + ")"

    def setArg(self, expr):
        self.arg = expr

    def getDescendantVarsAndSetters(self):
        """
        Recursively extract the non-composite expressions in this problem
        I.e. actual variables (either fixed values or truly variable)
        :return: a list of tuples of (variable, 1-argument method that can be called to replace the variable)
        """
        returnVal = []
        addDescVarOrRecurse(returnVal, self.arg, self.setArg)
        return returnVal

class SinExpression(UnaryExpression):
    def __init__(self, arg):
        self.operatorTxt = "sin"
        super(SinExpression, self).__init__(arg)

    def __repr__(self):
        return "<SinExpression: arg " + repr(self.arg) + ">"

    def getValue(self, context):
        if self.arg.getValue(context) is not None:
            print("Getting value for sine expression: " + str(math.sin(self.arg.getValue(context))))
            return math.sin(self.arg.getValue(context))
        else:
            return None

    def setValue(self, value, context):
        if self.arg.getValue(context):
            if value == math.sin(self.arg.getValue(context)):
                pass # but overconstrained
            else:
                print("Error! " + self.name + " is overconstrained")
        else:
            # Check for domain error
            if -1 <= value <= 1:
                self.arg.setValue(math.asin(value), context)
            else:
                print("Error! " + self.name + " set to value outside function domain (" + str(value) + ")")

class CosExpression(UnaryExpression):
    def __init__(self, arg):
        self.operatorTxt = "cos"
        super(CosExpression, self).__init__(arg)

    def __repr__(self):
        return "<CosExpression: arg " + repr(self.arg) + ">"

    def getValue(self, context):
        if self.arg.getValue(context) is not None:
            return math.cos(self.arg.getValue(context))
        else:
            return None

    def setValue(self, value, context):
        if self.arg.getValue(context):
            if value == math.cos(self.arg.getValue(context)):
                pass # but overconstrained
            else:
                print("Error! " + self.name + " is overconstrained")
        else:
            # Check for domain error
            if -1 <= value <= 1:
                self.arg.setValue(math.acos(value), context)
            else:
                print("Error! " + self.name + " set to value outside function domain (" + str(value) + ")")

class TanExpression(UnaryExpression):
    def __init__(self, arg):
        self.operatorTxt = "tan"
        super(TanExpression, self).__init__(arg)

    def __repr__(self):
        return "<TanExpression: arg " + repr(self.arg) + ">"

    def getValue(self, context):
        if self.arg.getValue(context) is not None:
            return math.tan(self.arg.getValue(context))
        else:
            return None

    def setValue(self, value, context):
        if self.arg.getValue(context):
            if value == math.tan(self.arg.getValue(context)):
                pass # but overconstrained
            else:
                print("Error! " + self.name + " is overconstrained")
        else:
            # Check for domain error
            #if -1 <= value <= 1:
                self.arg.setValue(math.atan(value), context)
            #else:
            #    print("Error! " + self.name + " set to value outside function domain (" + str(value) + ")")


####################################################################################
# Binary (2 arguments)
class BinaryExpression(CompositeExpression):
    def __init__(self, argA, argB):
        self.setArgA(argA)
        self.setArgB(argB)
        super(BinaryExpression, self).__init__(self.getTextFormula(), [self.argA, self.argB])

    def setArgA(self, expr):
        self.argA = expr

    def setArgB(self, expr):
        self.argB = expr

    def getTextFormula(self):
        return "(" + self.argA.name + " " + self.operatorSymbol + " " + self.argB.name + ")"

    def getDescendantVarsAndSetters(self):
        """
        Recursively extract the non-composite expressions in this problem
        I.e. actual variables (either fixed values or truly variable)
        :return: a list of tuples of (variable, 1-argument method that can be called to replace the variable)
        """
        returnVal = []
        addDescVarOrRecurse(returnVal, self.argA, self.setArgA)
        addDescVarOrRecurse(returnVal, self.argB, self.setArgB)
        return returnVal

class SumExpression(BinaryExpression):
    def __init__(self, addandA, addandB):
        self.operatorSymbol = '+'
        super(SumExpression, self).__init__(addandA, addandB)

    def __repr__(self):
        return "<SumExpression: addand A " + repr(self.argA) + ", addand B " + repr(self.argB) + ">"

    def getValue(self, context):
        if self.argA.getValue(context) is not None and self.argB.getValue(context) is not None:
            return self.argA.getValue(context) + self.argB.getValue(context)
        else:
            return None

    def setValue(self, value, context):
        a = self.argA.getValue(context)
        b = self.argB.getValue(context)
        if a:
            if b: # a,b
                if value==a+b:
                    pass # but overconstrained
                else:
                    print("Error! " + self.name + " is overconstrained")
            else: # a => b
                self.argB.setValue(value-a, context)
        else:
            if b: #b => a
                self.argA.setValue(value-b, context)
            else: # neither => can't do anything
                pass

class DifferenceExpression(BinaryExpression):
    def __init__(self, addand, subtractand):
        self.operatorSymbol = '-'
        super(DifferenceExpression, self).__init__(addand, subtractand)

    def __repr__(self):
        return "<DifferenceExpression: addand " + repr(self.argA) + ", subtractand " + repr(self.argB) + ">"

    def getValue(self, context):
        if self.argA.getValue(context) is not None and self.argB.getValue(context) is not None:
            return self.argA.getValue(context) - self.argB.getValue(context)
        else:
            return None

    def setValue(self, value, context):
        a = self.argA.getValue(context)
        b = self.argB.getValue(context)
        if a:
            if b: # a,b
                if value==a-b:
                    pass # but overconstrained
                else:
                    print("Error! " + self.name + " is overconstrained")
            else: # a => b
                self.argB.setValue(a-value, context)
        else:
            if b: #b => a
                self.argA.setValue(value+b, context)
            else: # neither => can't do anything
                pass

class ProductExpression(BinaryExpression):
    def __init__(self, multiplicanda, multiplicandb):
        self.operatorSymbol = '*'
        super(ProductExpression, self).__init__(multiplicanda, multiplicandb)

    def __repr__(self):
        return "<ProductExpression: multiplicand A " + repr(self.argA) + ", multiplicand B " + repr(self.argB) + ">"

    def getValue(self, context):
        if self.argA.getValue(context) is not None and self.argB.getValue(context) is not None:
            return self.argA.getValue(context) * self.argB.getValue(context)
        else:
            return None

    def setValue(self, value, context):
        a = self.argA.getValue(context)
        b = self.argB.getValue(context)
        if a:
            if b: # a,b
                if value==a*b:
                    pass # but overconstrained
                else:
                    print("Error! " + self.name + " is overconstrained")
            else: # a => b
                self.argB.setValue(value/a, context)
        else:
            if b: #b => a
                self.argA.setValue(value/b, context)
            else: # neither => can't do anything
                pass

class QuotientExpression(BinaryExpression):
    def __init__(self, numerator, denominator):
        self.operatorSymbol = '/'
        super(QuotientExpression, self).__init__(numerator, denominator)

    def __repr__(self):
        return "<QuotientExpression: numerator " + repr(self.argA) + ", denominator " + repr(self.argB) + ">"

    def getValue(self, context):
        if self.argA.getValue(context) is not None and self.argB.getValue(context) is not None:
            return self.argA.getValue(context) / self.argB.getValue(context)
        else:
            return None

    def setValue(self, value, context):
        n = self.argA.getValue(context)
        d = self.argB.getValue(context)
        if n:
            if d: # a,b
                if value==n/d:
                    pass # but overconstrained
                else:
                    print("Error! " + self.name + " is overconstrained")
            else: # n => d
                self.argB.setValue(n/value, context)
        else:
            if d: #d => n
                self.argA.setValue(value*d, context)
            else: # neither => can't do anything
                pass

class PowerExpression(BinaryExpression):
    def __init__(self, base, exponent):
        self.operatorSymbol = '^'
        super(PowerExpression, self).__init__(base, exponent)

    def __repr__(self):
        return "<PowerExpression: base " + repr(self.argA) + ", exponent " + repr(self.argB) + ">"

    def getValue(self, context):
        if self.argA.getValue(context) is not None and self.argB.getValue(context) is not None:
            return self.argA.getValue(context) ** self.argB.getValue(context)
        else:
            return None

    def setValue(self, value, context):
        base = self.argA.getValue(context)
        exp = self.argB.getValue(context)
        if base:
            if exp: # a,b
                if value==base**exp:
                    pass # but overconstrained
                else:
                    print("Error! " + self.name + " is overconstrained")
            else: # base => exp
                self.argB.setValue(math.ln(value)/math.ln(base), context)
        else:
            if exp: #exp => base
                self.argA.setValue(value**(1/exp), context) # TODO allow multiple solutions...
            else: # neither => can't do anything
                pass

