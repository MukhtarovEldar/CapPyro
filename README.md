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
**Note**: `expr*` indicates zero or more occurrences of the `expr`, and `expr+` indicates that at least one occurrence of the `expr` is required.

**statements**: `NEWLINE* expr (NEWLINE+ expr)* NEWLINE*`

- **expr** -- Represents an expression.
  - `VAR ID EQ expr` - Assignment of a variable.
  - `comp-expr ((AND | OR) comp-expr)*` - Logical expressions combining comparison expressions.

- **comp-expr** -- Represents a comparison expression.
  - `NOT comp-expr` - A negated comparison expression.
  - `arith-expr ((ISEQ | LT | GT | LEQ | GEQ) arith-expr)*` - Comparison of arithmetic expressions using comparison operators (ISEQ, LT, GT, LEQ, GEQ).

- **arith-expr** -- Represents an arithmetic expression.
  - `term ((PLUS | MINUS) term)*` - Addition or subtraction of terms.

- **term** -- Represents a term in an expression.
  - `factor ((MULT | DIV | DOT) factor)*` - Multiplication, division, or dot operation of factors.

- **factor** -- Represents a factor in an arithmetic expression.
  - `(PLUS | MINUS)* factor` - Unary plus or minus.
  - `power` - A power operation.

- **power** -- Represents a power operation.
  - `call (POW factor)*` - Exponentiation of an atom by a factor.

- **call** -- Represents a function call allowing for passing arguments.
  - `atom (LPAR (expr (COMMA expr)*)* RPAR)*` - A call to a function passing zero or more arguments enclosed in parentheses.

- **atom** -- Represents the basic building blocks of expressions.
  - `INT | FLOAT | STRING | ID ` - Integer, floating-point number, string, or identifier.
  - `LPAR expr RPAR` - An expression enclosed in parentheses.
  - `if-expr` - An if-else statement.
  - `while-expr` - A while-loop statement.
  - `for-expr` - A for-loop statement.
  - `func-def` - A function definition statement.
  - `list-expr` - A list creation expression.

- **if-expr** -- Represents an if-else statement.
  <br>&nbsp; &nbsp; &nbsp; &nbsp;`IF expr THEN` - Initiates an if-else block.
  <br>&nbsp; &nbsp; &nbsp; &nbsp;`expr`
  <br>&nbsp; &nbsp; &nbsp; &nbsp;`(ELIF expr THEN)*` - Optional expression for the `ELIF` branches.
  - `expr` 
  <br>`(ELSE expr)*` - Optional expression for the `ELSE` branch.
  <br>`expr`
  <br>`END` - Marks the end of the if-else statement.


- **while-expr** -- Represents a while-loop statement.
  - `WHILE expr THEN expr NEWLINE statements END` - A loop that continues while a condition is true.

- **for-expr** -- Represents a for-loop statement.
  - `FOR ID EQ expr TO expr (STEP expr)* THEN expr NEWLINE statements END` - A loop that iterates from an initial value to a final value with an optional step value (defaulting to 1 if not provided).

- **func-def** -- Represents the definition of a user-defined function.
  - `FUNC (ID)* LPAR (ID (COMMA ID)*)* RPAR COLON expr NEWLINE statements END` - Definition of a function with an identifier, a list of parameters, and a body expression.

- **list-expr** -- Represents a list creation expression.
  - `LSQUARE (expr (COMMA expr)*)* RSQUARE` - A list creation by specifying its elements, separated by commas, enclosed in square brackets.

### Special Keywords
The following keywords are reserved and may not be used as variable or function name:
```
AND     COLON   COMMA   ELSE	ELIF	END     
FOR     FUNC    IF      NOT     OR      PRINT
STEP    THEN	TO      VAR	WHILE
```


