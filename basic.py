DIGITS = "0123456789"

TOK_INT		 = 'INT'
TOK_FLOAT    = 'FLOAT'
TOK_PLUS     = 'PLUS'
TOK_MINUS    = 'MINUS'
TOK_MULT     = 'MULT'
TOK_DIV      = 'DIV'
TOK_LPAR     = 'LPAR'
TOK_RPAR     = 'RPAR'

class Error:
    def __init__(self, name, details):
        self.name = name
        self.details = details

    def as_string(self):
        return f'{self.name}: {self.details}'
    
class illegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class Token:
    def __init__ (self, type_, value = None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
class Lex:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.cur_char = None

    def advance(self):
        self.pos += 1
        self.cur_char = self.text[self.pos] if self.pos < len(self.text) else None

    def createTokens(self):
        tokens = []

        while self.cur_char != None:
            if self.cur_char in ' \r\n\t':
                None
            elif self.cur_char in DIGITS:
                tokens.append(self.createNumber())
            elif self.cur_char == '+':
                tokens.append(Token(TOK_PLUS))
            elif self.cur_char == '-':
                tokens.append(Token(TOK_MINUS))
            elif self.cur_char == '*':
                tokens.append(Token(TOK_MULT))
            elif self.cur_char == '/':
                tokens.append(Token(TOK_DIV))
            elif self.cur_char == '(':
                tokens.append(Token(TOK_LPAR))
            elif self.cur_char == ')':
                tokens.append(Token(TOK_RPAR))
            else:
                char = self.cur_char
                self.advance()
                return [], illegalCharError(char)
            self.advance()
        return Token, None
            
    def createNumber(self):
        str = ''
        dot_cnt = 0

        while self.cur_char != None and self.cur_char in DIGITS + '.':
            if self.cur_char == '.':
                if dot_cnt == 1:
                    break
                dot_cnt += 1
                str += '.'
            else:
                str += self.cur_char
            self.advance()
        if dot_cnt == 0:
            return Token(TOK_INT, int(str))
        else:
            return Token(TOK_FLOAT, float(str))
        
def run(text):
    lex = Lex(text)
    tokens, error = lex.createTokens()

    return tokens, error