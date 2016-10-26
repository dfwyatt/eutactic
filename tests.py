from parsedproblem import ParsedProblem


def test_orbits_numerical():
    # Get the problem
    p = ParsedProblem("examples/orbits.prob")
    # Get the default variable settings
    solveContext = p.defaultContext.copy()
    divider(1)
    p.print(solveContext)
    # Solve with the default var vals and print the results
    p.solve(context=solveContext, refContext=False)
    divider(2)
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
    divider(3)
    p.print(solveContext)

    divider(4)
    p.solve(context=solveContext, refContext=oldContext)



def divider(item):
    print(str(item) + "*" * 40)


if __name__ == '__main__':
    test_orbits_numerical()