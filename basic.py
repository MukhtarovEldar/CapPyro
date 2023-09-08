from highlight_range import *

import string

DIGITS = "0123456789"
ALPHA = string.ascii_letters
ALNUM = ALPHA + DIGITS


# -------------- ERROR ----------------

class Error:
    def __init__(self, pos_beg, pos_end, error_name, details):
        self.pos_beg = pos_beg
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def to_string(self):
        return f"{self.error_name}: {self.details}\n" \
               f"File {self.pos_beg.name}, line {self.pos_beg.line + 1}\n" \
               f"{highlight_range(self.pos_beg.text, self.pos_beg, self.pos_end)}"


class IllegalCharError(Error):
    def __init__(self, pos_beg, pos_end, details):
        super().__init__(pos_beg, pos_end, 'Illegal Character', details)


class ExpectedCharError(Error):
    def __init__(self, pos_beg, pos_end, details):
        super().__init__(pos_beg, pos_end, 'Expected Character', details)


class SyntaxError(Error):
    def __init__(self, pos_beg, pos_end, details=''):
        super().__init__(pos_beg, pos_end, 'Invalid Syntax', details)


class RTError(Error):
    def __init__(self, pos_beg, pos_end, details, context):
        super().__init__(pos_beg, pos_end, 'Runtime Error', details)
        self.context = context

    def to_string(self):
        traceback = self.generate_traceback()
        return f"{traceback}{self.error_name}: {self.details}\n" \
               f"{highlight_range(self.pos_beg.text, self.pos_beg, self.pos_end)}"

    def generate_traceback(self):
        result = ''
        pos = self.pos_beg
        ctx = self.context

        while ctx:
            result = f'  File {pos.name}, line {str(pos.line + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result


# --------------- POSITION ----------------

class Position:
    def __init__(self, index, line, col, name, text):
        self.index = index
        self.line = line
        self.col = col
        self.name = name
        self.text = text

    def advance(self, current_char=None):
        self.index += 1
        self.col += 1

        if current_char == '\n':
            self.line += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.col, self.name, self.text)


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
    def __init__(self, type_, value=None, pos_beg=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_beg:
            self.pos_beg = pos_beg.copy()
            self.pos_end = pos_beg.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def is_match(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


# ----------------- LEXER --------------------

OPERATORS = {
    '+': TOK_PLUS,
    '-': TOK_MINUS,
    '*': TOK_MULT,
    '/': TOK_DIV,
    '^': TOK_POW,
    '(': TOK_LPAR,
    ')': TOK_RPAR,
}


class Lex:
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.pos = Position(-1, 0, -1, name, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def create_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.create_number())
            elif self.current_char in ALPHA:
                tokens.append(self.create_id())
            elif self.current_char in OPERATORS:
                tokens.append(self.create_operator())
            elif self.current_char == '(':
                tokens.append(self.create_token(TOK_LPAR))
            elif self.current_char == ')':
                tokens.append(self.create_token(TOK_RPAR))
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
                pos_beg = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_beg, self.pos, "'" + char + "'")

        tokens.append(Token(TOK_EOF, pos_beg=self.pos))
        return tokens, None

    def create_number(self):
        num_str = ''
        dot_count = 0
        pos_beg = self.pos.copy()

        while self.current_char is not None and (self.current_char in DIGITS or (self.current_char == '.' and dot_count == 0)):
            if self.current_char == '.':
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOK_INT, int(num_str), pos_beg, self.pos)
        else:
            return Token(TOK_FLOAT, float(num_str), pos_beg, self.pos)

    def create_id(self):
        id_str = ''
        pos_beg = self.pos.copy()

        while self.current_char is not None and (self.current_char in ALNUM or self.current_char == '_'):
            id_str += self.current_char
            self.advance()

        tok_type = TOK_KEYWORD if id_str in KEYWORDS else TOK_ID
        return Token(tok_type, id_str, pos_beg, self.pos)

    def create_operator(self):
        pos_beg = self.pos.copy()
        operator = self.current_char
        self.advance()
        return Token(OPERATORS[operator], pos_beg=pos_beg, pos_end=self.pos)

    def create_token(self, tok_type):
        pos_beg = self.pos.copy()
        self.advance()
        return Token(tok_type, pos_beg=pos_beg, pos_end=self.pos)

    def create_not_equals(self):
        pos_beg = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TOK_NEQ, pos_beg=pos_beg, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_beg, self.pos, "'=' (after '!')")

    def create_equals(self):
        tok_type = TOK_EQ
        pos_beg = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOK_ISEQ

        return Token(tok_type, pos_beg=pos_beg, pos_end=self.pos)

    def create_less_than(self):
        tok_type = TOK_LT
        pos_beg = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOK_LEQ

        return Token(tok_type, pos_beg=pos_beg, pos_end=self.pos)

    def create_greater_than(self):
        tok_type = TOK_GT
        pos_beg = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOK_GEQ

        return Token(tok_type, pos_beg=pos_beg, pos_end=self.pos)


# ---------------- NODES ---------------------

class ASTNode:
    def __init__(self, pos_beg, pos_end):
        self.pos_beg = pos_beg
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class NumberNode(ASTNode):
    def __init__(self, tok):
        super().__init__(tok.pos_beg, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f"{self.tok}"


class VarAccessNode(ASTNode):
    def __init__(self, var_name_tok):
        super().__init__(var_name_tok.pos_beg, var_name_tok.pos_end)
        self.var_name_tok = var_name_tok

    def __repr__(self):
        return f"{self.var_name_tok}"


class VarAssignNode(ASTNode):
    def __init__(self, var_name_tok, value_node):
        super().__init__(var_name_tok.pos_beg, value_node.pos_end)
        self.var_name_tok = var_name_tok
        self.value_node = value_node

    def __repr__(self):
        return f"(VarAssignNode: {self.var_name_tok} = {self.value_node})"


class BinOpNode(ASTNode):
    def __init__(self, left_node, operator_token, right_node):
        super().__init__(left_node.pos_beg, right_node.pos_end)
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node} {self.operator_token} {self.right_node})"


class UnaryOpNode(ASTNode):
    def __init__(self, operator_token, node):
        super().__init__(operator_token.pos_beg, node.pos_end)
        self.operator_token = operator_token
        self.node = node

    def __repr__(self):
        return f"({self.operator_token}{self.node})"


# -------------------- PARSE RESULT -------------------------

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_cnt = 0

    def register_advancement(self):
        self.advance_cnt += 1

    def register(self, res):
        self.advance_cnt += res.advance_cnt
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_cnt == 0:
            self.error = error
        return self


# --------------- PARSER -------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_tok = self.tokens[self.tok_index]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TOK_EOF:
            return res.failure(SyntaxError(
                self.current_tok.pos_beg,
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
                return res.failure(SyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    "Expected ')'"))

        return res.failure(SyntaxError(
            tok.pos_beg,
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

        if self.current_tok.is_match(TOK_KEYWORD, 'NOT'):
            operator_token = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res

            return res.success(UnaryOpNode(operator_token, node))

        node = res.register(self.bin_op(self.arith_expr, (TOK_ISEQ, TOK_NEQ, TOK_LT, TOK_GT, TOK_LEQ, TOK_GEQ)))

        if res.error:
            return res.failure(SyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(' or 'NOT'"
            ))

        return res.success(node)

    def expr(self):
        res = ParseResult()

        if self.current_tok.is_match(TOK_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOK_ID:
                return res.failure(SyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    "Expected identifier"))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOK_EQ:
                return res.failure(SyntaxError(
                    self.current_tok.pos_beg,
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
            return res.failure(SyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-' or '('"))

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        func_b = func_b or func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            operator_token = self.current_tok
            res.register_advancement()
            self.advance()

            right = res.register(func_b())
            if res.error:
                return res

            left = BinOpNode(left, operator_token, right)

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
        self.pos_beg = None
        self.pos_end = None
        self.context = None

    def set_pos(self, pos_beg=None, pos_end=None):
        self.pos_beg = pos_beg
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subtract(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multiply(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def divide(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_beg, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None

    def exponentiate(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def equals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None

    def not_equals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None

    def less_than(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def greater_than(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def less_than_or_equal(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None

    def greater_than_or_equal(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None

    def logical_and(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None

    def logical_or(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None

    def logical_not(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_beg, self.pos_end)
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
    def execute(self, node, context):
        method_name = f'execute_{type(node).__name__}'
        method = getattr(self, method_name, self.no_execute_method)
        return method(node, context)

    def no_execute_method(self, node, context):
        raise Exception(f'No execute_{type(node).__name__} method defined')

    @staticmethod
    def execute_NumberNode(node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_beg, node.pos_end))

    @staticmethod
    def execute_VarAccessNode(node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_beg,
                node.pos_end,
                f"'{var_name}' is not defined",
                context))

        value = value.copy().set_pos(node.pos_beg, node.pos_end)
        return res.success(value)

    def execute_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.execute(node.value_node, context))
        if res.error:
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def execute_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.execute(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.execute(node.right_node, context))
        if res.error:
            return res

        error = None
        result = None

        if node.operator_token.type == TOK_PLUS:
            result, error = left.add(right)
        elif node.operator_token.type == TOK_MINUS:
            result, error = left.subtract(right)
        elif node.operator_token.type == TOK_MULT:
            result, error = left.multiply(right)
        elif node.operator_token.type == TOK_DIV:
            result, error = left.divide(right)
        elif node.operator_token.type == TOK_POW:
            result, error = left.exponentiate(right)
        elif node.operator_token.type == TOK_ISEQ:
            result, error = left.equals(right)
        elif node.operator_token.type == TOK_NEQ:
            result, error = left.not_equals(right)
        elif node.operator_token.type == TOK_LT:
            result, error = left.less_than(right)
        elif node.operator_token.type == TOK_GT:
            result, error = left.greater_than(right)
        elif node.operator_token.type == TOK_LEQ:
            result, error = left.less_than_or_equal(right)
        elif node.operator_token.type == TOK_GEQ:
            result, error = left.greater_than_or_equal(right)
        elif node.operator_token.is_match(TOK_KEYWORD, 'AND'):
            result, error = left.logical_and(right)
        elif node.operator_token.is_match(TOK_KEYWORD, 'OR'):
            result, error = left.logical_or(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_beg, node.pos_end))

    def execute_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.execute(node.node, context))
        if res.error:
            return res

        error = None

        if node.operator_token.type == TOK_MINUS:
            number, error = number.multiply(Number(-1))
        elif node.operator_token.is_match(TOK_KEYWORD, 'NOT'):
            number, error = number.logical_not()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_beg, node.pos_end))


# ----------------- RUN ---------------------

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run_program(name, text):
    lexer = Lex(name, text)
    tokens, lex_error = lexer.create_tokens()
    if lex_error:
        return None, lex_error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.execute(ast.node, context)

    return result.value, result.error
