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
TOK_EOF = 'EOF'
TOK_COMMA = 'COMMA'
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
    'FUNC'
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

