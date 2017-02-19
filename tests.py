from objects import ObjectTestProblem
from parsedproblem import ParsedProblem

def divider(item):
    print("*" * 10 + str(item) + "*" * 40)

###############################################################
# Tests

def test_orbits_numerical():
    """
    Test the ability to start solving a problem from a previous solution
    :return:
    """
    divider("Loading problem")
    # Get the problem
    p = ParsedProblem("examples/orbits.prob")
    # Get the default variable settings
    divider("Default variable settings")
    solveContext = p.defaultContext.copy()
    p.print(solveContext)
    divider("Solving with default var vals")
    # Solve with the default var vals and print the results
    p.solve(context=solveContext, refContext=False)
    divider("Solutions")
    p.print(solveContext)
    # Store the old var vals and reset the solve context
    oldContext = solveContext
    solveContext = p.defaultContext.copy()
    # Reset the problem: set r_m to be an output, and set period_day to be 1
    # Find the right variables
    r_m = [x for x in p.exprs if x.name=="r_m"][0]
    period_day = [x for x in p.exprs if x.name=="period_day"][0]
    #print(r_m)
    # Set the values
    r_m.setValue(None, solveContext)
    period_day.setValue(2, solveContext)
    divider("New re-set var vals")
    p.print(solveContext)

    divider("Solving with new var vals")
    p.solve(context=solveContext, refContext=oldContext)
    divider("Solutions")
    p.print(solveContext)
    divider("End")

def test_objects():
    testprob = ObjectTestProblem()
    print(testprob)
    testprob.solve()

if __name__ == '__main__':
    test_objects()
