# ---------------- NODES ---------------------

class ASTNode:
    def __init__(self, pos_beg, pos_end):
        self.pos_beg = pos_beg
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class NumberNode(ASTNode):
    def __init__(self, tok):
        super().__init__(tok.pos_beg, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f"{self.tok}"


class VarAccessNode(ASTNode):
    def __init__(self, var_name_tok):
        super().__init__(var_name_tok.pos_beg, var_name_tok.pos_end)
        self.var_name_tok = var_name_tok

    def __repr__(self):
        return f"{self.var_name_tok}"


class VarAssignNode(ASTNode):
    def __init__(self, var_name_tok, value_node):
        super().__init__(var_name_tok.pos_beg, value_node.pos_end)
        self.var_name_tok = var_name_tok
        self.value_node = value_node

    def __repr__(self):
        return f"(VarAssignNode: {self.var_name_tok} = {self.value_node})"


class BinOpNode(ASTNode):
    def __init__(self, left_node, operator_token, right_node):
        super().__init__(left_node.pos_beg, right_node.pos_end)
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node} {self.operator_token} {self.right_node})"


class UnaryOpNode(ASTNode):
    def __init__(self, operator_token, node):
        super().__init__(operator_token.pos_beg, node.pos_end)
        self.operator_token = operator_token
        self.node = node

    def __repr__(self):
        return f"({self.operator_token}{self.node})"


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_beg = self.cases[0][0].pos_beg
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end