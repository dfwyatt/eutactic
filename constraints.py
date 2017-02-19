from NIbase import addDescVarOrRecurse
from abc import abstractmethod
from abc import ABCMeta
import math
import numpy as np

__author__ = 'David Wyatt'


class Constraint(metaclass=ABCMeta):
    def __init__(self, name, *exprs):
        self.name = name

    @abstractmethod
    def propagate(self, context):
        pass

    @abstractmethod
    def getTextFormula(self):
        pass

    def numExprs(self):
        return len(self.getExprs())

    def getName(self):
        return self.name

    def getUndefinedExprs(self, context):
        exprlist = []
        for childexpr in self.getExprs():
            exprlist.extend(childexpr.getUndefinedExprs(context))
        return exprlist

    def numUndefinedExprs(self, context):
        return len(self.getUndefinedExprs(context))

    @abstractmethod
    def copy(self):
        pass

    @abstractmethod
    def getExprs(self):
        pass


class EqualityConstraint(Constraint):
    def __init__(self, name, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        super(EqualityConstraint, self).__init__(name, self.lhs, self.rhs)

    def propagate(self, context):
        if self.lhs.getValue(context) is None:
            if self.rhs.getValue(context) is None:
                #print("Error! " + name + " is underconstrained")
                pass
            else:
                self.lhs.setValue(self.rhs.getValue(context), context)
        else:
            if self.rhs.getValue(context) is None:
                self.rhs.setValue(self.lhs.getValue(context), context)
            else:
                # Values on both sides - check if they're equal...
                if abs(self.lhs.getValue(context) - self.rhs.getValue(context)) <= 10*np.finfo(float).eps:
                    # Everything's fine, just continue
                    pass
                else:
                    print("Error! " + self.name + " (" + self.getTextFormula() + ") is overconstrained - lhs = " + str(self.lhs.getValue(context)) + ", rhs = " + str(self.rhs.getValue(context)))
                    return False
        return True

    def __repr__(self):
        return "<EqualityConstraint " + self.getName() + ": lhs " + repr(self.lhs) + ", rhs " + repr(self.rhs) + ">"

    def getTextFormula(self):
        return self.lhs.getName() + " = " + self.rhs.getName()

    def copy(self):
        returnval = EqualityConstraint(self.name, self.lhs.copy(), self.rhs.copy())
        return returnval

    def setLhs(self, expr):
        self.lhs = expr

    def setRhs(self, expr):
        self.rhs = expr

    def getDescendantVarsAndSetters(self):
        """
        Recursively extract the non-composite expressions in this problem
        I.e. actual variables (either fixed values or truly variable)
        :return: a list of tuples of (variable, 1-argument method that can be called to replace the variable)
        """
        returnVal = []
        addDescVarOrRecurse(returnVal, self.lhs, self.setLhs)
        addDescVarOrRecurse(returnVal, self.rhs, self.setRhs)
        return returnVal

    def getExprs(self):
        return [self.lhs, self.rhs]

##############################################################################
# Definitions below here are left over from a previous approach and are not guaranteed to work!

class SumConstraint(Constraint):
    def __init__(self, name, lhs, addenda, addendb):
        self.name = name
        self.lhs = lhs
        self.addandA = addenda
        self.addandB = addendb
        super(SumConstraint, self).__init__(name, self.lhs, self.addandA, self.addandB)

    def __repr__(self):
        return "<SumConstraint: lhs " + repr(self.lhs) + ", addand A " + repr(self.addandA) + ", addand B " + repr(self.addandB) + ">"

    def propagate(self, context):
        l = self.lhs.getValue()
        a = self.addandA.getValue()
        b = self.addandB.getValue()
        if l:
            if a:
                if b: # l,a,b
                    if l==a+b:
                        pass # but overconstrained
                    else:
                        print("Error! " + self.name + " is overconstrained")
                        return False
                else: # l,a => b
                    self.addandB.setValue(l-a)
            else:
                if b: #l,b => a
                    self.addandA.setValue(l-b)
                else: # l only
                    pass
        else: # not l
            if a:
                if b: # a,b => l
                    self.lhs.setValue(a+b)
                else: # a only
                    pass
            else: # no l, no a
                pass
        return True

    def getTextFormula(self):
        return "(" + self.lhs.name + ") = (" + self.addandA.name + ") + (" + self.addandB.name + ")"


class ProductConstraint(Constraint):
    def __init__(self, name, lhs, multiplicandA, multiplicandB):
        self.name = name
        self.lhs = lhs
        self.multiplicandA = multiplicandA
        self.multiplicandB = multiplicandB
        super(ProductConstraint, self).__init__(name, self.lhs, self.multiplicandA, self.multiplicandB)

    def __repr__(self):
        return "<ProductConstraint: lhs " + repr(self.lhs) + ", multiplicand A " + repr(self.multiplicandA) + ", multiplicand B " + repr(self.multiplicandB) + ">"

    def propagate(self, context):
        l = self.lhs.getValue()
        a = self.multiplicandA.getValue()
        b = self.multiplicandB.getValue()
        if l:
            if a:
                if b: # l,a,b
                    if l==a*b:
                        pass # but overconstrained
                    else:
                        print("Error! " + self.name + " is overconstrained")
                        return False
                else: # l,a => b
                    self.multiplicandB.setValue(l/a)
            else:
                if b: #l,b => a
                    self.multiplicandA.setValue(l/b)
                else: # l only
                    pass
        else: # not l
            if a:
                if b: # a,b => l
                    self.lhs.setValue(a*b)
                else: # a only
                    pass
            else: # no l, no a
                pass
        return True

    def getTextFormula(self):
        return "(" + self.lhs.name + ") = (" + self.multiplicandA.name + ") * (" + self.multiplicandB.name + ")"


class PowerConstraint(Constraint):
    def __init__(self, name, lhs, base, exponent):
        self.name = name
        self.lhs = lhs
        self.base = base
        self.exponent = exponent
        super(PowerConstraint, self).__init__(name, self.lhs, self.base, self.exponent)

    def __repr__(self):
        return "<PowerConstraint: lhs " + repr(self.lhs) + ", base " + repr(self.base) + ", exponent " + repr(self.exponent) + ">"

    def propagate(self, context):
        l = self.lhs.getValue()
        b = self.base.getValue()
        e = self.exponent.getValue()
        if l:
            if b:
                if e: # l,b,e
                    if l==b**e:
                        pass # but overconstrained
                    else:
                        print("Error! " + self.name + " is overconstrained")
                        return False
                else: # l,b => e
                    self.exponent.setValue(math.ln(l)/math.ln(b))
            else:
                if e: #l,e => b
                    self.base.setValue(l**(1/e)) # TODO allow multiple solutions...
                else: # l only
                    pass
        else: # not l
            if b:
                if e: # b,e => l
                    self.lhs.setValue(b**e)
                else: # b only
                    pass
            else: # no l, no b
                pass
        return True

    def getTextFormula(self):
        return "(" + self.lhs.name + ") = (" + self.base.name + ")**(" + self.exponent.name + ")"