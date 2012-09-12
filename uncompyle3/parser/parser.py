from uncompyle3.utils.spark import GenericASTBuilder
from .astnode import ASTNode
from .pplogic import PostProcessLogic


# Empty function, used as argument when adding custom rules
nop_func = lambda self, args: None


class Parser(GenericASTBuilder):

    def __init__(self):
        self.added_rules = set()
        GenericASTBuilder.__init__(self, ASTNode, "stmts")

    def p_grammar(self, args):
        """
        stmts ::= stmts sstmt
        stmts ::= sstmt
        sstmt ::= stmt
        stmt ::= call_stmt
        call_stmt ::= expr POP_TOP
        designator ::= STORE_NAME
        kwarg ::= LOAD_CONST expr
        compare ::= expr expr COMPARE_OP
        """

    def p_expr(self, args):
        """
        expr ::= call_function
        expr ::= LOAD_NAME
        expr ::= LOAD_CONST
        expr ::= binary_expr
        expr ::= binary_subscr
        expr ::= unary_expr
        expr ::= unary_not
        expr ::= cmp
        expr ::= logic_expr

        binary_expr ::= expr expr binary_op
        binary_op ::= BINARY_POWER
        binary_op ::= BINARY_MULTIPLY
        binary_op ::= BINARY_DIVIDE
        binary_op ::= BINARY_FLOOR_DIVIDE
        binary_op ::= BINARY_TRUE_DIVIDE
        binary_op ::= BINARY_MODULO
        binary_op ::= BINARY_ADD
        binary_op ::= BINARY_SUBTRACT
        binary_op ::= BINARY_LSHIFT
        binary_op ::= BINARY_RSHIFT
        binary_op ::= BINARY_AND
        binary_op ::= BINARY_XOR
        binary_op ::= BINARY_OR

        binary_subscr ::= expr expr BINARY_SUBSCR

        unary_expr ::= expr unary_op
        unary_op ::= UNARY_POSITIVE
        unary_op ::= UNARY_NEGATIVE
        unary_op ::= UNARY_INVERT

        unary_not ::= expr UNARY_NOT

        cmp ::= compare

        logic_expr ::= expr logic_op expr
        logic_op ::= JUMP_IF_TRUE_OR_POP
        logic_op ::= POP_JUMP_IF_TRUE
        logic_op ::= JUMP_IF_FALSE_OR_POP
        logic_op ::= POP_JUMP_IF_FALSE
        """

    def p_assign(self, args):
        """
        stmt ::= assign
        assign ::= expr designator
        """

    def p_augmented_assign(self, args):
        """
        stmt ::= augassign
        augassign ::= expr expr inplace_op designator

        inplace_op ::= INPLACE_POWER
        inplace_op ::= INPLACE_MULTIPLY
        inplace_op ::= INPLACE_FLOOR_DIVIDE
        inplace_op ::= INPLACE_TRUE_DIVIDE
        inplace_op ::= INPLACE_MODULO
        inplace_op ::= INPLACE_ADD
        inplace_op ::= INPLACE_SUBTRACT
        inplace_op ::= INPLACE_LSHIFT
        inplace_op ::= INPLACE_RSHIFT
        inplace_op ::= INPLACE_AND
        inplace_op ::= INPLACE_XOR
        inplace_op ::= INPLACE_OR
        """

    def parse(self, tokens):
        self.add_custom_rules(tokens)
        ast = GenericASTBuilder.parse(self, tokens)
        pp_logic = PostProcessLogic()
        pp_logic.repair(ast)
        return ast

    def add_custom_rules(self, tokens):
        new_rules = set()
        for token in tokens:
            if token.type != 'CALL_FUNCTION':
                continue
            # Low byte indicates number of positional paramters,
            # high byte number of positional parameters
            args_pos = token.attr & 0xff
            args_kw = (token.attr >> 8) & 0xff
            pos_args_line = '' if args_pos == 0 else ' {}'.format(' '.join('expr' for _ in range(args_pos)))
            kw_args_line = '' if args_kw == 0 else ' {}'.format(' '.join('kwarg' for _ in range(args_kw)))
            rule = 'call_function ::= expr{}{} CALL_FUNCTION'.format(pos_args_line, kw_args_line)
            new_rules.add(rule)
        new_rules.difference_update(self.added_rules)
        for rule in new_rules:
            self.addRule(rule, nop_func)
        self.added_rules.update(new_rules)



#    def p_custom(self, args):
#        """
#        call_function ::= expr CALL_FUNCTION
#        """
