from highlight_range import *

import string

DIGITS = "0123456789"
ALPHA = string.ascii_letters
ALNUM = ALPHA + DIGITS


# -------------- ERROR ----------------

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        # result = f'{self.error_name}: {self.details}\n'
        # result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        # result += '\n\n' + highlight_range(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return f"{self.error_name}: {self.details}\n" \
               f"File {self.pos_start.fn}, line {self.pos_start.ln + 1}\n" \
               f"{highlight_range(self.pos_start.ftxt, self.pos_start, self.pos_end)}"


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Expected Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        # result = self.generate_traceback()
        # result += f'{self.error_name}: {self.details}'
        # result += '\n\n' + highlight_range(self.pos_start.ftxt, self.pos_start, self.pos_end)
        traceback = self.generate_traceback()
        return f"{traceback}{self.error_name}: {self.details}\n" \
               f"{highlight_range(self.pos_start.ftxt, self.pos_start, self.pos_end)}"

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result


# --------------- POSITION ----------------

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


# ---------------- TOKENS ---------------------

TOK_INT = 'INT'
TOK_FLOAT = 'FLOAT'
TOK_ID = 'ID'
TOK_KEYWORD = 'KEYWORD'
TOK_PLUS = 'PLUS'
TOK_MINUS = 'MINUS'
TOK_MULT = 'MULT'
TOK_DIV = 'DIV'
TOK_POW = 'POW'
TOK_EQ = 'EQ'
TOK_ISEQ = 'ISEQ'
TOK_NEQ = 'NEQ'
TOK_LT = 'LT'
TOK_GT = 'GT'
TOK_LEQ = 'LEQ'
TOK_GEQ = 'GEQ'
TOK_LPAR = 'LPAR'
TOK_RPAR = 'RPAR'
TOK_EOF = 'EOF'

KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT'
]


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


# ----------------- LEXER --------------------

class Lex:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def createTokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.create_number())
            elif self.current_char in ALPHA:
                tokens.append(self.create_id())
            elif self.current_char == '+':
                tokens.append(Token(TOK_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TOK_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TOK_MULT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TOK_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TOK_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TOK_EQ, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TOK_LPAR, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOK_RPAR, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.create_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.create_equals())
            elif self.current_char == '<':
                tokens.append(self.create_less_than())
            elif self.current_char == '>':
                tokens.append(self.create_greater_than())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TOK_EOF, pos_start=self.pos))
        return tokens, None

    def create_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOK_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TOK_FLOAT, float(num_str), pos_start, self.pos)

    def create_id(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in ALNUM + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TOK_KEYWORD if id_str in KEYWORDS else TOK_ID
        return Token(tok_type, id_str, pos_start, self.pos)

    def create_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TOK_NEQ, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def create_equals(self):
        tok_type = TOK_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOK_ISEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def create_less_than(self):
        tok_type = TOK_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOK_LEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def create_greater_than(self):
        tok_type = TOK_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOK_GEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


# ---------------- NODES ---------------------

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


# -------------------- PARSE RESULT -------------------------

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


# --------------- PARSER -------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TOK_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '+', '-', '*' or '/'"))
        return res

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOK_INT, TOK_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TOK_ID:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TOK_LPAR:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TOK_RPAR:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ')'"))

        return res.failure(InvalidSyntaxError(
            tok.pos_start,
            tok.pos_end,
            "Expected int, float, identifier, '+', '-' or '('"))

    def power(self):
        return self.bin_op(self.atom, (TOK_POW,), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOK_PLUS, TOK_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TOK_MULT, TOK_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TOK_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (TOK_ISEQ, TOK_NEQ, TOK_LT, TOK_GT, TOK_LEQ, TOK_GEQ)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(' or 'NOT'"
            ))

        return res.success(node)

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TOK_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOK_ID:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected identifier"))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOK_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected '='"))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((TOK_KEYWORD, "AND"), (TOK_KEYWORD, "OR"))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-' or '('"))

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)


# ----------- RUNTIME RESULT ----------------

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


# ---------------- VALUES -------------------

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None

    def powered_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None

    def get_comparison_neq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def get_comparison_leq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None

    def get_comparison_geq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None

    def and_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None

    def or_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None

    def not_by(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)


# --------------- CONTEXT ------------------

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


# ------------- SYMBOL TABLE ----------------

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


# ------------- INTERPRETER -----------------

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start,
                node.pos_end,
                f"'{var_name}' is not defined",
                context))

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TOK_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TOK_MINUS:
            result, error = left.subtracted_by(right)
        elif node.op_tok.type == TOK_MULT:
            result, error = left.multiplied_by(right)
        elif node.op_tok.type == TOK_DIV:
            result, error = left.divided_by(right)
        elif node.op_tok.type == TOK_POW:
            result, error = left.powered_by(right)
        elif node.op_tok.type == TOK_ISEQ:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TOK_NEQ:
            result, error = left.get_comparison_neq(right)
        elif node.op_tok.type == TOK_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TOK_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TOK_LEQ:
            result, error = left.get_comparison_leq(right)
        elif node.op_tok.type == TOK_GEQ:
            result, error = left.get_comparison_geq(right)
        elif node.op_tok.matches(TOK_KEYWORD, 'AND'):
            result, error = left.and_with(right)
        elif node.op_tok.matches(TOK_KEYWORD, 'OR'):
            result, error = left.or_with(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == TOK_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(TOK_KEYWORD, 'NOT'):
            number, error = number.not_by()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))


# ----------------- RUN ---------------------

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run(fn, text):
    lexer = Lex(fn, text)
    tokens, error = lexer.createTokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
