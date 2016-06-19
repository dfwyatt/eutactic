# Reusable objects for equation-solver
# David Wyatt, 21 February 2016

# Each NIobject has local variables, which can take various values, and local equations/constraints, which always hold but only refer to that object's variables
# It also has a link to its parent class, and a name
# TODO Make it possible for an object to have child objects
from constraints import EqualityConstraint
from equationsolver import Problem
from expressions import ScalarVariable
__author__ = 'David Wyatt'

class NIObject:
    def __init__(self, name, niclass):
        self.niclass = niclass
        self.name = name
        self.variables = [var.copy() for var in self.niclass.variables]
        for constr in self.niclass.constrs:
            # Need to find the instance variables corresponding to the variables in the class definion
            pass
        self.constrs = []

    def __repr__(self):
        return "<NIObject: name " + self.name + ", class " + repr(self.niclass) + ", variables " + repr(self.variables) + ", constraints " + repr(self.constrs) + ">"

# An NIclass is basically the template for an NIobject - it has a list of variables that each object of that class inherits, and likewise constraints
class NIClass:
    def __init__(self, name, vars, constrs):
        self.name = name
        # Store a list of variables associated with the class
        self.variables = vars
        self.constrs = constrs

    def __repr__(self):
        return "<NIClass: name " + self.name + ", variables " + repr(self.variables) + ", constraints " + repr(self.constrs) + ">"


class ObjectTestProblem(Problem):
    def __init__(self):
        super(ObjectTestProblem, self).__init__("Object test problem")
        testVar1 = ScalarVariable("TestVar1", 10)
        testVar2 = ScalarVariable("TestVar2")

        # Create a class definition as a test
        testClass = NIClass("Test class", [testVar1, testVar2], [EqualityConstraint("Test constraint", testVar1, testVar2)])

        # Create an object from that class
        testObj = NIObject("Test object", testClass)

        print(testObj)

        #testConstr = EqualityConstraint("Test constraint", testVar1, testVar2)
        #self.addConstr(testConstr)

        # f = ScalarVariable("F")
        # m = ScalarVariable("m", 68)
        # a = ScalarVariable("a", 9.81)
        # self.addConstr(EqualityConstraint("Test constraint 2", f, testVar2))
        # #n2law = ProductConstraint("Newton's 2nd law", f, m, a)
        # self.addConstr(EqualityConstraint("Newton's 2nd law", f, ProductExpression(m, a)))
        #
        # ph = ScalarVariable("pH", 7)
        # concHp = ScalarVariable("[H+]")
        # self.addConstr(EqualityConstraint("pH definition", concHp, PowerExpression(FixedValue(10), ProductExpression(FixedValue(-1), ph))))



if __name__ == "__main__":
    testprob = ObjectTestProblem()

    print(testprob)
    testprob.solve()

    #testprob.draw("problem_structure.png")
