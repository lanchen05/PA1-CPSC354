from lark import Lark, Transformer
import math
import sys

# Load the grammar from grammar.lark (run this file from the Assignment1 folder)
with open("grammar.lark", "r") as grammar_file:
    grammar = grammar_file.read()

# Create a Lark parser from the grammar
parser = Lark(grammar, parser='lalr')


# Step 2: turn the parse tree into an AST.
# Each method name matches a "-> name" alias in grammar.lark.
# "items" is the list of already-converted children.
class CalcTransformer(Transformer):
    def number(self, items):
        text = str(items[0])
        if text.isdigit():
            return ('num', int(text))
        return ('num', float(text))

    def neg(self, items):
        return ('neg', items[0])

    def add(self, items):
        return ('add', items[0], items[1])

    def sub(self, items):
        return ('sub', items[0], items[1])

    def mul(self, items):
        return ('mul', items[0], items[1])

    def pow(self, items):
        return ('pow', items[0], items[1])

    def log(self, items):
        # log items[0] base items[1]
        return ('log', items[0], items[1])


# Step 3: evaluate the AST (calls itself on the children)
def evaluate(ast):
    if ast[0] == 'num':
        return ast[1]
    elif ast[0] == 'neg':
        return -evaluate(ast[1])
    elif ast[0] == 'add':
        return evaluate(ast[1]) + evaluate(ast[2])
    elif ast[0] == 'sub':
        return evaluate(ast[1]) - evaluate(ast[2])
    elif ast[0] == 'mul':
        return evaluate(ast[1]) * evaluate(ast[2])
    elif ast[0] == 'pow':
        base = evaluate(ast[1])
        exponent = evaluate(ast[2])
        if base == 0 and exponent < 0:
            raise ValueError("0 cannot be raised to a negative power")
        if base < 0 and exponent != int(exponent):
            raise ValueError("negative base with a non-integer exponent")
        return base ** exponent
    elif ast[0] == 'log':
        x = evaluate(ast[1])
        base = evaluate(ast[2])
        if x <= 0:
            raise ValueError("log argument must be positive")
        if base <= 0 or base == 1:
            raise ValueError("log base must be positive and not 1")
        # round to hide tiny floating-point errors (e.g. 2.9999999999999996)
        return round(math.log(x) / math.log(base), 10)
    else:
        raise ValueError(f"Unknown operation: {ast}")


# Put the three steps together: text -> parse tree -> AST -> number
def calculate(input_string):
    calc_transformer = CalcTransformer()
    cst = parser.parse(input_string)
    ast = calc_transformer.transform(cst)
    result = evaluate(ast)
    # show whole-number results without ".0" (3.0 -> 3)
    if isinstance(result, float) and result.is_integer() and abs(result) < 1e15:
        result = int(result)
    return result


# Main execution
if __name__ == "__main__":
    input_string = " ".join(sys.argv[1:])
    try:
        print(calculate(input_string))
    except ValueError as error:
        print("Math error:", error)
    except Exception as error:
        print("Syntax error:", str(error).splitlines()[0])
