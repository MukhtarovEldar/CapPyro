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
        return result

class illegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

# --------------- POSITION ----------------

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
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

class Token:
    def __init__(self, type_, value = None):
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
                return [], illegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def createNumber(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOK_INT, int(num_str))
        else:
            return Token(TOK_FLOAT, float(num_str))

# ----------------- RUN ---------------------

def run(fn, text):
    lexer = Lex(fn, text)
    tokens, error = lexer.createTokens()

    return tokens, error
