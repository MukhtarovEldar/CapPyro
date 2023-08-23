from highlight_range import *

DIGITS = "0123456789"


# -------------- ERROR ----------------

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + highlight_range(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


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
TOK_PLUS = 'PLUS'
TOK_MINUS = 'MINUS'
TOK_MULT = 'MULT'
TOK_DIV = 'DIV'
TOK_LPAR = 'LPAR'
TOK_RPAR = 'RPAR'
TOK_EOF = 'EOF'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

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
                tokens.append(self.createNumber())
            elif self.current_char == '+':
                tokens.append(Token(TOK_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TOK_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TOK_MULT))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TOK_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TOK_LPAR))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOK_RPAR))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TOK_EOF))
        return tokens, None

    def createNumber(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOK_INT, int(num_str))
        else:
            return Token(TOK_FLOAT, float(num_str))


# ---------------- NODE ---------------------

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


# --------------- PARSER -------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = 1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        return res

    def factor(self):
        tok = self.current_tok

        if tok.type in (TOK_INT, TOK_FLOAT):
            self.advance()
            return NumberNode(tok)

    def term(self):
        return self.bin_op(self.factor, (TOK_MULT, TOK_DIV))

    def expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS))

    def bin_op(self, func, ops):
        left = func()

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advance()
            right = func()
            left = BinOpNode(left, op_tok, right)

        return left


# ----------------- RUN ---------------------

def run(fn, text):
    lexer = Lex(fn, text)
    tokens, error = lexer.createTokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast, None
