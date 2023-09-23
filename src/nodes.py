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


class StringNode(ASTNode):
    def __init__(self, tok):
        super().__init__(tok.pos_beg, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f"{self.tok}"


class VarAccessNode(ASTNode):
    def __init__(self, var_name_token):
        super().__init__(var_name_token.pos_beg, var_name_token.pos_end)
        self.var_name_token = var_name_token

    def __repr__(self):
        return f"{self.var_name_token}"


class VarAssignNode(ASTNode):
    def __init__(self, var_name_token, value_node):
        super().__init__(var_name_token.pos_beg, value_node.pos_end)
        self.var_name_token = var_name_token
        self.value_node = value_node

    def __repr__(self):
        return f"(VarAssignNode: {self.var_name_token} = {self.value_node})"


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


class IfNode(ASTNode):
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        super().__init__(self.cases[0][0].pos_beg, (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end)


class WhileNode(ASTNode):
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        super().__init__(self.condition_node.pos_beg, self.body_node.pos_end)


class ForNode(ASTNode):
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        super().__init__(self.var_name_token.pos_beg, self.body_node.pos_end)


class FuncDefNode(ASTNode):
    def __init__(self, var_name_token, arg_name_tokens, body_node):
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node

        if self.var_name_token:
            super().__init__(self.var_name_token.pos_beg, self.body_node.pos_end)
        elif len(self.arg_name_tokens) > 0:
            super().__init__(self.arg_name_tokens[0].pos_beg, self.body_node.pos_end)
        else:
            super().__init__(self.body_node.pos_beg, self.body_node.pos_end)


class CallNode(ASTNode):
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        if len(self.arg_nodes) > 0:
            super().__init__(self.node_to_call.pos_beg, self.arg_nodes[len(self.arg_nodes) - 1].pos_end)
        else:
            super().__init__(self.node_to_call.pos_beg, self.node_to_call.pos_end)


class ListNode(ASTNode):
    def __init__(self, element_nodes, pos_beg, pos_end):
        self.element_nodes = element_nodes

        super().__init__(pos_beg, pos_end)
