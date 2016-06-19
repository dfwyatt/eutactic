# Syntax for defining Eutactic problems
Eutactic problem (.prob) files can be defined straightforwardly in plain text - a number of examples are included in the "examples" directory. 

## Variables
Variables can be defined implicitly, by using them in an equation (see below). For example:

`a = b + c     # defines variables a, b, c`

Variables can also be defined in isolation and given a default initial value using `:=`:

`height := 2`

This will cause them to be an input by default in the interactive GUI.

The name for a variable can be any contiguous sequence of letters, numbers and underscores (`_`), as long as the first character is not a number.

## Equations

An equation is defined using conventional text-based mathematical symbols, with the crucial fact that amongst the symbols must be *precisely one* equals character `=`:

```
(a+3)+5=10*15
a = b
b = c
V = EMF - I*R_int
V = I*R_ext
EMF=9
z+9+z = 3
r = cos(0)
expt_two = e + pi "Constant test"
```

Currently supported mathematical operators are:
* `+`, `-`, `*`, `/`
* `^` for to-the-power-of
* `sin`, `cos`, `tan`

More will be implemented in the future!

## Constants
Constants are symbols that have a numerical value that does not change.

**Numerical literals** are the simplest form of constant - pure numbers!

**Symbolic constants** are useful to define reusable values. They are defined using two `=` characters:

`hours_per_day == 24`

Two symbolic constants are built into the language: `pi` and `e`.

## Comments and equation titles
**Line comments** are started using the `#` character - the rest of the line is ignored. There is no syntax for block comments.

**Equation titles** allow an equation to be given an identifier for future reference (if an equation is not titled explicitly, its title is the line number in its file). This is done using a string in `"` directly after the equation definition:

`F = m * a "Newton's 3rd law"`

## Importing other files

The contents of another .prob file may be imported into the current file using `import`:

`import("constants.prob")`
