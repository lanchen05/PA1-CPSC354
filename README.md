# Assignment 1 – Calculator

**Author:** Landon Chen

## Files

| File | Purpose |
|---|---|
| `calculator_cfg.py` | Builds the AST and evaluates it |
| `grammar.lark` | Unambiguous grammar used by Lark |
| `specs.md` | Detailed specifications |


## Usage

Run from this folder, with the expression in quotes:

```
python calculator_cfg.py "1 + 2 * 3"
```

## Supported operations

`+`, `-`, `*`, `^`, unary `-`, `log x base b`, and parentheses.

| Input | Output |
|---|---|
| `1+2*3` | 7 |
| `2^3^2` | 512 |
| `-3^2` | -9 |
| `log 8 base 2 + 1` | 4 |
