# CapPyro

CapPyro is a simple Python-based interpreter. Although it shares many similarities with Python, it adopts a unique convention where all special keywords are expressed in CAPITAL letters, setting it apart from conventional Python interpreters.

## Getting Started

To get started with CapPyro, you need to have Python installed on your system. You can clone the CapPyro repository and run the interpreter using the provided scripts.

```bash
git clone https://github.com/MukhtarovEldar/CapPyro.git
cd CapPyro
python shell.py
```

## Expression Structure
**Note**: `(expr)*` indicates optional expressions.

- **expr** -- Represents an expression.
  - `VAR ID EQ expr` - Assignment of a variable.
  - `comp-expr ((AND | OR) comp-expr)*` - Logical expressions combining comparison expressions.

- **comp-expr** -- Represents a comparison expression.
  - `NOT comp-expr` - A negated comparison expression.
  - `arith-expr ((ISEQ | LT | GT | LEQ | GEQ) arith-expr)*` - Comparison of arithmetic expressions using comparison operators (ISEQ, LT, GT, LEQ, GEQ).

- **arith-expr** -- Represents an arithmetic expression.
  - `term ((PLUS | MINUS) term)*` - Addition or subtraction of terms.

- **term** -- Represents a term in an arithmetic expression.
  - `factor ((MULT | DIV) factor)*` - Multiplication or division of factors.

- **factor** -- Represents a factor in an arithmetic expression.
  - `(PLUS | MINUS)* factor` - Unary plus or minus.
  - `power` - A power operation.

- **power** -- Represents a power operation.
  - `atom (POW factor)*` - Exponentiation of an atom by a factor.

- **atom** -- Represents the basic building blocks of expressions.
  - `INT | FLOAT | ID` - Integer, floating-point number, or identifier.
  - `LPAR expr RPAR` - An expression enclosed in parentheses.
  - `if-expr` - An if-else statement.

- **if-expr** -- Represents an if-else statement.
  - `IF expr THEN expr (ELIF expr THEN expr)* (ELSE expr)*` - Conditional statements with optional elif and else branches.

- **while-expr** -- Represents a while-loop statement.
  - `WHILE expr THEN expr` - A loop that continues while a condition is true.

- **for-expr** -- Represents a for-loop statement.
  - `FOR ID EQ expr TO expr (STEP expr)* THEN expr` - A loop that iterates from an initial value to a final value with an optional step value (defaulting to 1 if not provided).

### Special Keywords
The following keywords are reserved and may not be used as variable or function name:
```
AND     ELSE	ELIF	END     FOR     IF	NOT
OR      PRINT   STEP	THEN	TO      VAR	WHILE
```


