from .highlight_range import *

# ----------------- ERROR -----------------------

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

