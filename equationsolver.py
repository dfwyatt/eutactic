# Numerical infrastructure
# David Wyatt, 3 March 2015

from constraints import *
from expressions import *
import scipy.optimize
import numpy as np
__author__ = 'David Wyatt'

class Context:
    # A context is a set of variable-value bindings
    # The keys for the variable values are the variable names
    def __init__(self, varVals=None):
        if varVals is not None:
            self.varVals = dict(varVals)
        else:
            self.varVals = dict()

    def getValue(self, var):
        if var.name in self.varVals:
            return self.varVals[var.name]
        else:
            return None

    def setValue(self, var, value):
        self.varVals[var.name] = value

    def extendWithValues(self, additionalVals):
        # Return a copy of this dictionary with the extra values specified in the supplied dictionary
        copy = Context(self.varVals)
        for (var, val) in additionalVals:
            copy.setValue(var, val)
        return copy

    def __repr__(self):
        return "<Context: " + str(self.varVals) + ">"

    def copy(self):
        return Context(varVals = self.varVals)



class Problem:
    def __init__(self, name):
        self.name = name
        self.exprs = set()
        self.constrs = set()
        self.sequenced = False
        self.defaultContext = Context({})

    def addExpression(self, expr):
        if expr.isComposite():
            self.addExprs(*expr.getChildren())
        else:
            self.exprs.add(expr)
            self.defaultContext.setValue(expr, expr.value)

    def addExprs(self, *exprs):
        for expr in exprs:
            self.addExpression(expr)

    def addConstr(self, constr):
        self.constrs.add(constr)
        self.addExprs(*constr.exprs)

    def addConstrs(self, *constrs):
        for constr in constrs:
            self.addConstr(constr)

    def solve(self, context=False):
        print("********Solving")
        context = context or self.defaultContext
        # Iteratively attempt to assign values to every undefined ScalarValue
        # Try to sequence constrs first to solve in the right order
        # The sequence constraints were solved in, for future reference
        self.solveseq = []
        tempconstrlist = list(self.constrs)
        # Whether we've encountered a failure or not
        # Loop while there are still unsolved constraints
        while (len(tempconstrlist) > 0):
            # Beginning of pass
            foundANewConstr = False
            #print("****Start solve loop")
            # Loop over all constraints
            for constr in list(tempconstrlist):
                undefVars = constr.getUndefinedExprs(context)
                if len(undefVars) == 0:
                    # Fully constrained => check it's consistent
                    #print("Checking full-constrained constraint for consistency:", constr.name)
                    result = constr.propagate(context)
                    if not(result):
                        break
                    print("Checked \"" + constr.name + "\" and found it to be consistent")
                    # Admin
                    tempconstrlist.remove(constr)
                    self.solveseq.append(constr)
                    foundANewConstr = True
                elif len(undefVars) == 1:
                    # Next easiest case is if only 1 undefined expression
                    #print("Propagating constraint:", constr.name)
                    # Actually solve this constraint!
                    result = constr.propagate(context)
                    if not(result):
                        break
                    # Admin
                    tempconstrlist.remove(constr)
                    self.solveseq.append(constr)
                    print("Solved \"" + constr.name + "\" analytically to give " + str(undefVars[0].name) + " = " + str(context.getValue(undefVars[0])))
                    foundANewConstr = True
                elif len(set(undefVars)) == 1: # use set() to remove duplicates
                    undefVarsSet = set(undefVars)
                    # Look out for cases where we have multiple copies of the same variable in a constraint!
                    #print("Detected a constraint where there are multiple copies of the same variable:", constr.name, constr.getTextFormula(), "(Variable: " + str(undefVars[0].name), ")")
                    print("Solving \"" + constr.name + "\" numerically due to multiple occurrences of " + undefVars[0].name + "...")
                    result = self.LSsolve([constr], context, undefVarsSet)
                    if not(result):
                        break
                    # Admin
                    tempconstrlist.remove(constr)
                    self.solveseq.append(constr)
                    print("Solved \"" + constr.name + "\" numerically to give " + str(undefVars[0].name) + " = " + str(context.getValue(undefVars[0])))
                    foundANewConstr = True
                else:
                    # Genuinely multiple undefined variables
                    # So leave it to the end...
                    pass
                # End of loop over all constraints
            if foundANewConstr == False:
                print("No more constraints to solve one-var-at-a-time. " + str(len(tempconstrlist)) + " remaining constraints:")
                for txt in [constr.name + ": " + constr.getTextFormula() for constr in tempconstrlist]:
                    print(txt)
                # Now let's try the multi-variate least squares fitting...
                # Sanity check first - do we have enough variables?
                numConstrs = len(tempconstrlist)
                allUndefVars = set([item for constr in tempconstrlist for item in constr.getUndefinedExprs(context)])
                print(str(len(allUndefVars)) + " remaining undefined variables:", [var.name for var in allUndefVars])
                if numConstrs >= len(allUndefVars):
                    print("Number of remaining constraints >= number of undefined variables => try solving numerically!")
                    result = self.LSsolve(tempconstrlist, context, allUndefVars)
                    if not(result):
                        print("Error solving remaining constraints numerically - giving up.")
                        return False
                    print("Solved " + str([constr.name for constr in tempconstrlist]) + " numerically to give " + str([var.name + "=" + str(context.getValue(var)) for var in allUndefVars]))
                    tempconstrlist.clear()
                else:
                    print("Number of remaining constraints <= number of undefined variables => giving up.")
                    # TODO We may still be able to solve a subset of the equations...
                    return False
        self.sequenced = True
        return True

    def LSsolve(self, constrs, context, undefVars):
        #print("++++++++++++++++++++++++")
        # Solve one or more constraints by numerical optimisation
        # The first thing is to construct f(x) from each constraint, which will be LHS - RHS
        f_exprs = [DifferenceExpression(constr.lhs, constr.rhs) for constr in constrs]
        print("  Formula(e) whose roots are to be found:")
        [print("  " + f_expr.getTextFormula()) for f_expr in f_exprs]
        #print("Using SciPy leastsq.")
        # Make a list of all the undefined variables, which will be the "master" list defining the variable order
        varList = list(undefVars)
        # Construct an elaborate lambda expression for the function evaluation
        dictgen = lambda x: {(entry[0], entry[1]) for entry in zip(varList, x)}
        f = lambda x: [f_expr.getValue(context.extendWithValues(dictgen(x))) for f_expr in f_exprs]
        # Now the call to leastsq...
        result = scipy.optimize.leastsq(f, np.zeros(len(varList)))
        #print("All results from leastsq:", result) # [x, cov_x, infodict]
        print("  Numerical result:", str(result[0]))
        #print("+++++++++++++++++++++++++")
        # TODO for the moment just assume the value we get back is definitely the solution!
        [context.setValue(e[0], e[1]) for e in zip(varList, result[0])]
        return True

    def __repr__(self):
        return "<Problem: variables " + repr(self.exprs) + ", constraints " + repr(self.constrs) + ">"
        
    def print(self, context=False):
        print("---Problem structure---")
        print("Problem: " + self.name)
        print("----------Exprs:")
        for var in self.exprs:
            if context and context.getValue(var):
                print(var.name, ":", str(context.getValue(var)))
            else:
                print(repr(var))
        print("----------Constrs:")
        for con in self.constrs:
            print(con.getTextFormula())




class TestProblem(Problem):
    def __init__(self):
        super(TestProblem, self).__init__("Test problem")
        testVar1 = ScalarVariable("TestVar1", 10)
        testVar2 = ScalarVariable("TestVar2")
        testConstr = EqualityConstraint("Test constraint", testVar1, testVar2)
        self.addConstr(testConstr)

        f = ScalarVariable("F")
        m = ScalarVariable("m", 68)
        a = ScalarVariable("a", 9.81)
        self.addConstr(EqualityConstraint("Test constraint 2", f, testVar2))
        #n2law = ProductConstraint("Newton's 2nd law", f, m, a)
        self.addConstr(EqualityConstraint("Newton's 2nd law", f, ProductExpression(m, a)))

        ph = ScalarVariable("pH", 7)
        concHp = ScalarVariable("[H+]")
        self.addConstr(EqualityConstraint("pH definition", concHp, PowerExpression(FixedValue(10), ProductExpression(FixedValue(-1), ph))))



if __name__ == "__main__":
    testprob = TestProblem()

    print(testprob)
    testprob.solve()

    #testprob.draw("problem_structure.png")


