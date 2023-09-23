from .position import *
from .error import *
import string

DIGITS = "0123456789"
ALPHA = string.ascii_letters
ALNUM = ALPHA + DIGITS


# ---------------- TOKENS ---------------------

TOK_INT = 'INT'
TOK_FLOAT = 'FLOAT'
TOK_STR = 'STRING'
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
TOK_LSQUARE = 'LSQUARE'
TOK_RSQUARE = 'RSQUARE'
TOK_DOT = 'DOT'
TOK_EOF = 'EOF'
TOK_COMMA = 'COMMA'
TOK_NEWLINE = 'NEWLINE'
TOK_COLON = 'COLON'

KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELSE',
    'THEN',
    'ELIF',
    'WHILE',
    'FOR',
    'TO',
    'STEP',
    'FUNC',
    'END'
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
    '[': TOK_LSQUARE,
    ']': TOK_RSQUARE
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
            elif self.current_char in ';\n':
                tokens.append(Token(TOK_NEWLINE, pos_beg=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.create_number())
            elif self.current_char in ALPHA:
                tokens.append(self.create_id())
            elif self.current_char in OPERATORS:
                tokens.append(self.create_operator())
            elif self.current_char == '"':
                tokens.append(self.create_string())
            elif self.current_char == '.':
                tokens.append(self.create_dot_operator())
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
            elif self.current_char == ',':
                tokens.append(Token(TOK_COMMA, pos_beg=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TOK_COLON, pos_beg=self.pos))
                self.advance()
            else:
                pos_beg = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_beg, self.pos, "'" + char + "'")

        tokens.append(Token(TOK_EOF, pos_beg=self.pos))
        return tokens, None

    def create_number(self):
        num_str = ''
        dot_cnt = 0
        pos_beg = self.pos.copy()

        while self.current_char is not None and (
                self.current_char in DIGITS or (self.current_char == '.' and dot_cnt == 0)):
            if self.current_char == '.':
                dot_cnt += 1
            num_str += self.current_char
            self.advance()

        if dot_cnt == 0:
            return Token(TOK_INT, int(num_str), pos_beg, self.pos)
        else:
            return Token(TOK_FLOAT, float(num_str), pos_beg, self.pos)

    def create_string(self):
        new_str = ''
        pos_beg = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t',
            'b': '\b',
            'r': '\r'
        }

        while self.current_char is not None and (self.current_char != '"' or escape_character):
            if escape_character:
                escape_character = False
                new_str += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    new_str += self.current_char
            self.advance()

        self.advance()
        return Token(TOK_STR, new_str, pos_beg, self.pos)

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

    # def create_token(self, tok_type):
    #     pos_beg = self.pos.copy()
    #     self.advance()
    #     return Token(tok_type, pos_beg=pos_beg, pos_end=self.pos)

    def create_dot_operator(self):
        pos_beg = self.pos.copy()
        self.advance()
        if self.current_char == '[':
            return Token(TOK_DOT, pos_beg=pos_beg, pos_end=self.pos)
        return None, ExpectedCharError(pos_beg, self.pos, "'[' (after '.')")

    #   TODO: Add Remove, Pop, and other functions for lists

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
