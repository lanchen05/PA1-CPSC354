# Assignment 1 – Calculator Specifications

## 1. Overview

The program evaluates arithmetic expressions typed as text. It has three stages:

```
input string --(Lark LALR parser + grammar.lark)--> parse tree
             --(CalcTransformer)---------------------> AST (nested tuples)
             --(evaluate(), recursive)---------------> number
```

Files:

| File | Purpose |
|---|---|
| `grammar.lark` | Unambiguous CFG used by Lark to generate the parser |
| `calculator_cfg.py` | parse-tree-to-AST transformer, recursive evaluator, main block |
| `specs.md` | This document |

Supported operations: `+`, `-` (binary), `*`, `^`, unary `-`, `log e1 base e2`, parentheses, and integer/decimal numbers.

## 2. Grammar (`grammar.lark`)

The assignment's grammar (`exp -> exp op exp`) is ambiguous: `1+2*3` and `2^3^2` each have several parse trees. The ambiguity is removed by giving every precedence level its own rule, so the shape of the parse tree is forced to match the intended order of operations.

| Level (low → high) | Rule | Operators | Associativity |
|---|---|---|---|
| 1 | `exp` | `+`, `-` | left |
| 2 | `term` | `*` | left |
| 3 | `factor` | unary `-`, `log … base …` | prefix |
| 4 | `power` | `^` | right |
| 5 | `atom` | number, `( exp )` | – |

Key design decisions:

- **Left associativity** is encoded by left recursion: `exp: exp "+" term`. So `10-4-3 = (10-4)-3 = 3`.
- **Right associativity of `^`**: `power: atom "^" factor` recurses on the right, so `2^3^2 = 2^(3^2) = 512`.
- **Unary minus is weaker than `^`**: `factor: "-" factor` wraps a `power`, so `-2^2 = -(2^2) = -4`, the usual mathematical convention. Because the exponent is a `factor`, `2^-1 = 0.5` is also accepted.
- **`log e1 base e2`**: the first argument sits between the keywords `log` and `base`, so it can be any full `exp` (the `base` keyword unambiguously ends it). The second argument is a `factor`, so it extends over `^` and further prefix operators but stops at `+`, `-`, `*`. Hence `log 8 base 2 + 1 = (log 8 base 2) + 1 = 4`, and `2 * log 100 base 10 = 4`. To use a sum as the base, write parentheses: `log 8 base (1+1)`.
- Rules starting with `?` are inlined by Lark when they have a single child, so pass-through levels (`exp → term → factor → …`) do not add nodes to the parse tree.
- Rule aliases (`-> add`, `-> sub`, `-> mul`, `-> neg`, `-> log`, `-> pow`, `-> number`) name the tree nodes; these names are the transformer's method names.
- Whitespace is ignored (`%ignore WS`). Numbers use Lark's built-in `NUMBER` (integers, decimals, exponent notation). A leading minus is not part of a number; it is parsed as unary minus.

## 3. Code (`calculator_cfg.py`)

The file is run from the `Assignment1` folder, because it opens `grammar.lark` by name. It has three steps, each in its own piece of code, plus a small main block.

### 3.1 AST representation

An AST node is a tuple `(operator, child, child, ...)`, where children are again nodes:

| Node | Meaning |
|---|---|
| `('num', v)` | the number `v` (an int if the text is only digits, otherwise a float) |
| `('neg', x)` | `-x` |
| `('add' / 'sub' / 'mul', a, b)` | `a + b`, `a - b`, `a * b` |
| `('pow', a, b)` | `a ^ b` |
| `('log', a, b)` | `log a base b` |

Example: `1 + 2 * 3` becomes `('add', ('num', 1), ('mul', ('num', 2), ('num', 3)))`.

### 3.2 `CalcTransformer(Transformer)`

Step 2: converts the Lark parse tree into the AST. Lark calls the method whose name matches each rule alias in `grammar.lark` (`number`, `neg`, `add`, `sub`, `mul`, `pow`, `log`), starting from the leaves. Each method receives `items`, the list of its already-converted children, and returns the matching tuple. For example, `add(self, items)` returns `('add', items[0], items[1])`.

Parenthesised expressions need no method: the parentheses are dropped by Lark and the inner expression is passed up unchanged.

### 3.3 `evaluate(ast)`

Step 3: recursive evaluator. It looks at `ast[0]` (the operator):

- `'num'`: return the stored value (base case of the recursion).
- `'neg'`, `'add'`, `'sub'`, `'mul'`: call `evaluate` on the child(ren) and apply `-`, `+`, `-`, `*`.
- `'pow'`: evaluate both children, then compute `base ** exponent`. Raises `ValueError` for `0` to a negative power, and for a negative base with a non-integer exponent (which would otherwise give a complex number).
- `'log'`: evaluate both children, then compute `ln(x) / ln(base)`, rounded to 10 decimals to hide floating-point noise (e.g. `log 1000 base 10` would otherwise print `2.9999999999999996`). Raises `ValueError` if `x <= 0`, `base <= 0`, or `base == 1`.
- anything else: raise `ValueError("Unknown operation")`.

### 3.4 `calculate(input_string)` and the main block

- `calculate` ties the steps together: `parser.parse(text)` gives the parse tree (step 1, done by Lark from the grammar), `CalcTransformer().transform(tree)` gives the AST, and `evaluate(ast)` gives the number. A float result that is a whole number (e.g. `3.0` from `log 8 base 2`) is converted to an int, so it prints as `3`.
- The main block joins the command-line arguments into one string, calls `calculate`, and prints the result. Errors are printed instead of crashing: `ValueError` -> `Math error: ...`; any other exception (a Lark parse error) -> `Syntax error: ...`.

### 3.5 Program flow

```
python calculator_cfg.py 1 + 2 '*' 3
   -> parser.parse("1 + 2 * 3")             parse tree (Lark, using grammar.lark)
   -> CalcTransformer().transform(tree)    ('add', ('num', 1), ('mul', ('num', 2), ('num', 3)))
   -> evaluate(ast)                         7
   -> print(7)
```

## 4. Examples

| Input | Result | Why |
|---|---|---|
| `1 + 2 * 3` | 7 | `*` binds tighter than `+` |
| `10 - 4 - 3` | 3 | left-associative `-` |
| `2 ^ 3 ^ 2` | 512 | right-associative `^` |
| `-2 ^ 2` | -4 | `^` binds tighter than unary `-` |
| `2 ^ -1` | 0.5 | exponent may be a unary-minus expression |
| `2 - -3` | 5 | binary minus followed by unary minus |
| `log 8 base 2` | 3 | |
| `log 8 base 2 + 1` | 4 | base argument stops at `+` |
| `2 * log 100 base 10` | 4 | `log` allowed as a `*` operand |
| `log 8 base (1 + 1)` | 3 | parentheses for a compound base |
| `0 ^ -1` | Math error | division by zero |
| `log -1 base 2` | Math error | log of a non-positive number |
| `1 +` | Syntax error | incomplete expression |

## 5. Testing

The following checks were run and all pass: all rows of the table above; additionally `(1+2)*3 = 9`, `-(1+2)*3 = -9`, `- - 3 = 3`, `2 ^ log 8 base 2 = 8`, `log 2 + 6 base 2 = 3`, `3 * 4 - 2 * 5 = 2`, `1.5 * 2 = 3`, and the error cases `2 ^`, `log 8`, `1 2`, `log 8 base 1`, `(-8) ^ 0.5`.
