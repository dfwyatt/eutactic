# Reusable objects for equation-solver
# David Wyatt, 21 February 2016

# Each NIobject has local variables, which can take various values, and local equations/constraints, which always hold but only refer to that object's variables
# It also has a link to its parent class, and a name
# TODO Make it possible for an object to have child objects
from constraints import EqualityConstraint
from equationsolver import Problem
from expressions import ScalarVariable

__author__ = 'David Wyatt'

# An NIclass is basically the template for an NIobject - it has a list of variables that each object of that class inherits, and likewise constraints
class NIClass:
    def __init__(self, name, vars, constrs):
        self.name = name
        # Store a list of variables associated with the class
        self.variables = vars
        self.constrs = constrs

    def __repr__(self):
        return "<NIClass: name " + self.name + ", variables " + repr(self.variables) + ", constraints " + repr(self.constrs) + ">"


class NIObject:
    def __init__(self, name, niclass):
        self.niclass = niclass
        self.name = name
        self.variables = []
        [self.addVar(var.copy()) for var in self.niclass.variables]
        self.varnamesdict = {var.name: var for var in self.variables}
        self.constrs = []
        for classconstr in self.niclass.constrs:
            # Need to copy the class' constraints but replace the class' variables with the corresponding instance variables
            # First copy the constraint and add to list
            newconstr = classconstr.copy()
            self.constrs.append(newconstr)
            # Override the constraint's getName with a function that prepends this object's name
            newconstr.getName = lambda: self.getChildObjName(newconstr)
            # Now iterate through every non-composite expression
            for (var, varSetFunc) in newconstr.getDescendantVarsAndSetters():
                # Check if it refers to a class variable
                if var in self.niclass.variables:
                    # If so replace it
                    # Find the corresponding instance variable
                    varToReplaceWith = self.varnamesdict[var.name]
                    # And slot this in in place of the class variable...
                    varSetFunc(varToReplaceWith)

    def addVar(self, var):
        self.variables.append(var)
        # Override the variable's getName with a function that prepends this object's name
        # Let's see if this works...
        var.getName = lambda: self.getChildObjName(var)

    def getChildObjName(self, childObj):
        return self.name + "." + childObj.name

    def __repr__(self):
        return "<NIObject: name " + self.name + ", class " + repr(self.niclass) + ", variables " + repr(self.variables) + ", constraints " + repr(self.constrs) + ">"

    def getVar(self, varname):
        if varname in self.varnamesdict:
            return self.varnamesdict[varname]
        else:
            return None

