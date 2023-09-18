from .nodes import *
from .tokens import *
from .error import *


# -------------------- PARSE RESULT -------------------------

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_cnt = 0

    def register_advancement(self):
        self.advance_cnt += 1

    def register(self, res):
        self.advance_cnt += res.advance_cnt
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_cnt == 0:
            self.error = error
        return self


# --------------- PARSER -------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_tok = self.tokens[self.tok_index]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TOK_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                "Expected '+', '-', '*', '/' or '^'"))
        return res

    def expr(self):
        res = ParseResult()

        if self.current_tok.is_match(TOK_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOK_ID:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    "Expected identifier"))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOK_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    "Expected '='"))

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((TOK_KEYWORD, "AND"), (TOK_KEYWORD, "OR"))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                "Expected 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"))

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.is_match(TOK_KEYWORD, 'NOT'):
            operator_token = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res

            return res.success(UnaryOpNode(operator_token, node))

        node = res.register(self.bin_op(self.arith_expr, (TOK_ISEQ, TOK_NEQ, TOK_LT, TOK_GT, TOK_LEQ, TOK_GEQ)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', '[' or 'NOT'"
            ))

        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS, TOK_DOT))

    def term(self):
        return self.bin_op(self.factor, (TOK_MULT, TOK_DIV, TOK_DOT))
    # TODO: Correct the problem with DOT in AST --- ex. [1, 2, 3] + [[4].[0]] should print [1, 2, 3, 4]

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOK_PLUS, TOK_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TOK_POW,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TOK_LPAR:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TOK_RPAR:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_beg,
                        self.current_tok.pos_end,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', "
                        "'(', '[' or 'NOT' "))

                while self.current_tok.type == TOK_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TOK_RPAR:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_beg,
                        self.current_tok.pos_end,
                        f"Expected ',' or ')'"))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOK_INT, TOK_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type in TOK_STR:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TOK_ID:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TOK_LPAR:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TOK_RPAR:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    "Expected ')'"))

        elif tok.type == TOK_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        elif tok.is_match(TOK_KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.is_match(TOK_KEYWORD, 'FOR'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.is_match(TOK_KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.is_match(TOK_KEYWORD, 'FUNC'):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_beg,
            tok.pos_end,
            "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUN'"))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.is_match(TOK_KEYWORD, 'IF'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'IF'"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.is_match(TOK_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'THEN'"))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res
        cases.append((condition, expr))

        while self.current_tok.is_match(TOK_KEYWORD, 'ELIF'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            if not self.current_tok.is_match(TOK_KEYWORD, 'THEN'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    f"Expected 'THEN'"))

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.is_match(TOK_KEYWORD, 'ELSE'):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.is_match(TOK_KEYWORD, 'FOR'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'FOR'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOK_ID:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected identifier"))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOK_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected '='"))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.is_match(TOK_KEYWORD, 'TO'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'TO'"))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.is_match(TOK_KEYWORD, 'STEP'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.is_match(TOK_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'THEN'"))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.is_match(TOK_KEYWORD, 'WHILE'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'WHILE'"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.is_match(TOK_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'THEN'"))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.is_match(TOK_KEYWORD, 'FUNC'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected 'FUNC'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOK_ID:
            var_name_token = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TOK_LPAR:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    f"Expected '('"))
        else:
            var_name_token = None
            if self.current_tok.type != TOK_LPAR:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    f"Expected identifier or '('"))

        res.register_advancement()
        self.advance()
        arg_name_tokens = []

        if self.current_tok.type == TOK_ID:
            arg_name_tokens.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TOK_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TOK_ID:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_beg,
                        self.current_tok.pos_end,
                        f"Expected identifier"))

                arg_name_tokens.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TOK_RPAR:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    f"Expected ',' or ')'"))
        else:
            if self.current_tok.type != TOK_RPAR:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg,
                    self.current_tok.pos_end,
                    f"Expected identifier or ')'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOK_COLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected ':'"))

        res.register_advancement()
        self.advance()

        node_to_return = res.register(self.expr())
        if res.error:
            return res

        return res.success(FuncDefNode(
            var_name_token,
            arg_name_tokens,
            node_to_return
        ))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_beg = self.current_tok.pos_beg.copy()

        if self.current_tok.type != TOK_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_beg,
                self.current_tok.pos_end,
                f"Expected '['"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOK_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg, self.current_tok.pos_end,
                    "Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', "
                    "'[' or 'NOT' "
                ))

            while self.current_tok.type == TOK_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TOK_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_beg, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(
            element_nodes,
            pos_beg,
            self.current_tok.pos_end.copy()
        ))

    def bin_op(self, func_a, ops, func_b=None):
        func_b = func_b or func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            operator_token = self.current_tok
            res.register_advancement()
            self.advance()

            right = res.register(func_b())
            if res.error:
                return res

            left = BinOpNode(left, operator_token, right)

        return res.success(left)
