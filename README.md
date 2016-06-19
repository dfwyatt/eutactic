# Eutactic solver and GUI

Eutactic is a system for exploring mathematical relationships between numerical variables. These relationships may occur in engineering (especially early conceptual design), science, economics or other fields.

The idea behind Eutactic is to allow the user to define a "problem" as a set of **numerical variables** and **equations** relating those variables to one another, and then to choose a subset of the variables to be "inputs" and assess their effects on the remaining variables. Unlike most other numerical computing environments, the choice of input and output variables can be changed *at run-time*.

Correspondingly, in Eutactic interrelationships between variables are defined as true *equations* - not *formulae*, as in most other environments. As an example:
* Equation: a*x^2 + b*x + c = 0
* Formula: x = (-b + sqrt(b^2 - 4*a*c))/(2*a)

At present Eutactic is in early development, primarily focused on the solver core and a simple GUI. Long-term plans include integration with other numerical systems.

## Documentation
* [Syntax for defining .prob files](docs/problem_syntax.md)
