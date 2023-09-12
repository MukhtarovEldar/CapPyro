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