from .lexer import *
from .parser import *
from .values import *
from .error import *


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

    def execute_IfNode(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.execute(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.register(self.execute(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.execute(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)

    def execute_WhileNode(self, node, context):
        res = RTResult()

        while True:
            condition = res.register(self.execute(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.execute(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def execute_ForNode(self, node, context):
        res = RTResult()

        start_value = res.register(self.execute(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.execute(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.execute(node.step_value_node, context))
            if res.error:
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            res.register(self.execute(node.body_node, context))
            if res.error:
                return res

        return res.success(None)


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
