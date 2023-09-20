from .lexer import *
from .parser import *
from .error import *


# ---------------- VALUES -------------------

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()
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
        return None, self.illegal_operation(other)

    def subtract(self, other):
        return None, self.illegal_operation(other)

    def multiply(self, other):
        return None, self.illegal_operation(other)

    def divide(self, other):
        return None, self.illegal_operation(other)

    def exponentiate(self, other):
        return None, self.illegal_operation(other)

    def equals(self, other):
        return None, self.illegal_operation(other)

    def not_equals(self, other):
        return None, self.illegal_operation(other)

    def less_than(self, other):
        return None, self.illegal_operation(other)

    def greater_than(self, other):
        return None, self.illegal_operation(other)

    def less_than_or_equal(self, other):
        return None, self.illegal_operation(other)

    def greater_than_or_equal(self, other):
        return None, self.illegal_operation(other)

    def logical_and(self, other):
        return None, self.illegal_operation(other)

    def logical_or(self, other):
        return None, self.illegal_operation(other)

    def logical_not(self, other):
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    @staticmethod
    def is_true():
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(
            self.pos_beg, other.pos_end,
            'Illegal operation',
            self.context
        )


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.other = None
        self.pos_beg = None
        self.pos_end = None
        self.context = None

    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subtract(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multiply(self, other):
        if isinstance(other, String):
            return String(self.value * other.value).set_context(self.context), None
        elif isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def divide(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_beg, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def exponentiate(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def equals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def not_equals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def less_than(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def greater_than(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def less_than_or_equal(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def greater_than_or_equal(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def logical_and(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def logical_or(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def logical_not(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_beg, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)


Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def add(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multiply(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_beg, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_beg)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        arg_cnt_str = "argument" if len(arg_names) < 2 else "arguments"

        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_beg, self.pos_end,
                f"Function '{self}' expected {len(arg_names)} {arg_cnt_str}, but got {len(args)}.",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_beg, self.pos_end,
                f"Function '{self}' expected {len(arg_names)} {arg_cnt_str}, but got {len(args)}.",
                self.context
            ))

        return res.success(None)

    @staticmethod
    def populate_args(arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.error:
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.error:
            return res

        value = res.register(interpreter.execute(self.body_node, exec_ctx))
        if res.error:
            return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_beg, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error:
            return res

        return_value = res.register(method(exec_ctx))
        if res.error:
            return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined.')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_beg, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    #####################################

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get("value")))
        return RTResult().success(Number.null)

    execute_print.arg_names = ["value"]

    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))

    execute_input.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        lst = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(lst, List):
            return RTResult().failure(RTError(
                self.pos_beg, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        lst.elements.append(value)
        return RTResult().success(Number.null)

    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        lst = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(lst, List):
            return RTResult().failure(RTError(
                self.pos_beg, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_beg, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = lst.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.pos_beg, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)

    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RTError(
                self.pos_beg, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(RTError(
                self.pos_beg, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)

    execute_extend.arg_names = ["listA", "listB"]


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def add(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def subtract(self, other):
        # def lists_(a, b, result):
        #     for elem_a in a:
        #         tmp_lst = []
        #         for elem_b in b:

        def nested_lists(a, b, result):
            new_lst = a.elements.copy()
            for elem_b in b.elements:
                tmp_lst = List([])
                for elem_a in new_lst:
                    areLists = isinstance(elem_a, List) and isinstance(elem_b, List)
                    areNumbers = isinstance(elem_a, Number) and isinstance(elem_b, Number)
                    if areLists:
                        return nested_lists(elem_a, elem_b, result)
                    elif areNumbers:
                        if elem_a.value != elem_b.value:
                            tmp_lst.elements.append(elem_a)
                            # result.elements.append(tmp_lst)
                    else:
                        result.elements.append(elem_a)
                    if areLists:
                        result.elements.append(tmp_lst)
                new_lst = tmp_lst.copy()
                result = new_lst.copy()

        result = List([])
        if isinstance(other, List):
            nested_lists(self, other, result)
            return result, None
        else:
            return None, Value.illegal_operation(self, other)

    def multiply(self, other):
        if isinstance(other, Number):
            self.elements *= other.value
            return self, None
        else:
            return None, Value.illegal_operation(self, other)

    def indexed(self, other):
        if isinstance(other, List):
            try:
                if len(other.elements) != 1:
                    return None, InvalidSyntaxError(
                        other.pos_beg,
                        other.pos_end,
                        "Index variable must be a single integer"
                    )
                return self.elements[other.elements[0].value], None
            except:
                return None, RTError(
                    other.pos_beg, other.pos_end,
                    'Index out of bounds: Element at this index could not be retrieved from the list',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_beg, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'


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
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

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
    def execute_StringNode(node, context):
        return RTResult().success(String(node.tok.value).set_context(context).set_pos(node.pos_beg, node.pos_end))

    @staticmethod
    def execute_VarAccessNode(node, context):
        res = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_beg,
                node.pos_end,
                f"'{var_name}' is not defined",
                context))

        value = value.copy().set_pos(node.pos_beg, node.pos_end).set_context(context)
        return res.success(value)

    def execute_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_token.value
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
        elif node.operator_token.type == TOK_DOT:
            result, error = left.indexed(right)

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
        elements = []

        while True:
            condition = res.register(self.execute(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            elements.append(res.register(self.execute(node.body_node, context)))
            if res.error:
                return res

        return res.success(List(elements).set_context(context).set_pos(node.pos_beg, node.pos_end))

    def execute_ForNode(self, node, context):
        res = RTResult()
        elements = []

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
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            elements.append(res.register(self.execute(node.body_node, context)))
            if res.error:
                return res

        return res.success(List(elements).set_context(context).set_pos(node.pos_beg, node.pos_end))

    @staticmethod
    def execute_FuncDefNode(node, context):
        res = RTResult()

        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_beg,
                                                                                            node.pos_end)

        if node.var_name_token:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def execute_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.execute(node.node_to_call, context))
        if res.error:
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_beg, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.execute(arg_node, context)))
            if res.error:
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.error:
            return res
        return_value = return_value.copy().set_pos(node.pos_beg, node.pos_end).set_context(context)
        return res.success(return_value)

    def execute_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.execute(element_node, context)))
            if res.error:
                return res

        return res.success(List(elements).set_context(context).set_pos(node.pos_beg, node.pos_end))


# ----------------- RUN ---------------------

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("PRINT", BuiltInFunction.print)
global_symbol_table.set("INPUT", BuiltInFunction.input)
global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_table.set("IS_FUN", BuiltInFunction.is_function)
global_symbol_table.set("APPEND", BuiltInFunction.append)
global_symbol_table.set("POP", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)


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
