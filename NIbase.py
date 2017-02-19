def addDescVarOrRecurse(returnVal, expr, exprSetter):
    if expr.isComposite():
        returnVal.extend(expr.getDescendantVarsAndSetters())
    else:
        returnVal.append((expr, exprSetter))