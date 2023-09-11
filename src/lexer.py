from tokens import *
from position import *
from error import *
import string

DIGITS = "0123456789"
ALPHA = string.ascii_letters
ALNUM = ALPHA + DIGITS


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

        while self.current_char is not None and (
                self.current_char in DIGITS or (self.current_char == '.' and dot_count == 0)):
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
