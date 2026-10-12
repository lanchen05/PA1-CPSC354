# Assignment 1 – Calculator Specifications

## 1. Overview

The program evaluates an arithmetic expression given as text, e.g. `python calculator_cfg.py "1 + 2 * 3"`. It works in three steps:

```
text --(Lark parser from grammar.lark)--> parse tree
     --(CalcTransformer)----------------> AST (nested tuples)
     --(evaluate, recursive)------------> number
```

Supported: `+`, `-`, `*`, `^`, unary `-`, `log e1 base e2`, parentheses, integer and decimal numbers.

## 2. Grammar (`grammar.lark`)

The assignment's grammar (`exp -> exp op exp`) is ambiguous, e.g. `1+2*3` has several parse trees. The new grammar accepts the same language but has one rule per precedence level, so each input has exactly one parse tree:

| Level (low → high) | Rule | Operators | Associativity |
|---|---|---|---|
| 1 | `exp` | `+`, `-` | left |
| 2 | `term` | `*` | left |
| 3 | `factor` | unary `-`, `log … base …` | prefix |
| 4 | `power` | `^` | right |
| 5 | `atom` | number, `( exp )` | – |

- Left associativity comes from left recursion (`exp: exp "+" term`), so `10-4-3 = 3`.
- `^` is right-associative (`power: atom "^" factor`), so `2^3^2 = 512`.
- Unary minus binds weaker than `^`, so `-2^2 = -4`.
- In `log e1 base e2`, `e1` can be any `exp` (the `base` keyword ends it) and `e2` is a `factor`, so `log 8 base 2 + 1 = (log 8 base 2) + 1 = 4`. Use parentheses for a compound base: `log 8 base (1+1)`.
- The aliases (`-> add`, `-> mul`, …) name the tree nodes; they are the names of the transformer methods.

## 3. Code (`calculator_cfg.py`)

**AST.** Each node is a tuple `(operator, child, ...)`: `('num', v)`, `('neg', x)`, and `('add' | 'sub' | 'mul' | 'pow' | 'log', a, b)`. Example: `1 + 2 * 3` becomes `('add', ('num', 1), ('mul', ('num', 2), ('num', 3)))`.

**`CalcTransformer(Transformer)`** converts the parse tree into the AST. Lark calls the method matching each alias (`number`, `neg`, `add`, `sub`, `mul`, `pow`, `log`) from the leaves upward. Each method gets its converted children in `items` and returns the matching tuple. `number` returns an int if the text is only digits, otherwise a float.

**`evaluate(ast)`** computes the value recursively. A `'num'` node returns its value (base case). Every other node evaluates its children, then applies its operator. Checks: `pow` raises `ValueError` for `0` to a negative power and for a negative base with a non-integer exponent; `log` computes `ln(x) / ln(base)` (rounded to 10 decimals to hide floating-point noise) and raises `ValueError` if `x <= 0`, `base <= 0` or `base == 1`.

**`calculate(input_string)`** runs the three steps (`parser.parse`, `CalcTransformer().transform`, `evaluate`) and converts whole-number floats to ints, so `3.0` prints as `3`.

**Main block.** Joins the command-line arguments, calls `calculate` and prints the result. A `ValueError` prints `Math error: ...`; any other exception (a Lark parse error) prints `Syntax error: ...`.

## 4. Examples

| Input | Output | Why |
|---|---|---|
| `1 + 2 * 3` | 7 | `*` before `+` |
| `2 ^ 3 ^ 2` | 512 | `^` is right-associative |
| `-3 ^ 2` | -9 | `^` before unary `-` |
| `log 8 base 2 + 1` | 4 | base stops at `+` |
| `0 ^ -1` | Math error | 0 to a negative power |
| `1 +` | Syntax error | incomplete expression |
