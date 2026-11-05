"""Precedence, associativity, source errors and text-tree rendering contracts."""
import unittest

from kira_frontend.ast_nodes import ASTNode, format_ast
from kira_frontend.errors import SyntaxIssue
from kira_frontend.lexer import Lexer
from kira_frontend.parser_expressions import parse_cond, parse_expr


def tokens_for(source):
    tokens, issues = Lexer().lex(source)
    if issues:
        raise AssertionError(issues)
    return tuple(tokens)


def shape(node):
    return (node.label, tuple(map(shape, node.children)))


def leaf(label):
    return (label, ())


def binary(operator, left, right):
    return (f"BinOp {operator}", (left, right))


class ExpressionTests(unittest.TestCase):
    def test_precedence_in_both_orders(self):
        one, two, three = map(leaf, ("Int 1", "Int 2", "Int 3"))
        for low in ("+", "-"):
            for high in ("*", "/", "%"):
                for source, expected in (
                    (f"1 {low} 2 {high} 3", binary(low, one, binary(high, two, three))),
                    (f"1 {high} 2 {low} 3", binary(low, binary(high, one, two), three)),
                ):
                    with self.subTest(source=source):
                        tokens = tokens_for(source)
                        tree, end = parse_expr(tokens, 0)
                        self.assertEqual(shape(tree), expected)
                        self.assertEqual(end, len(tokens))

    def test_each_precedence_level_folds_left(self):
        eight, three, two = map(leaf, ("Int 8", "Int 3", "Int 2"))
        for operators in (("+", "-"), ("*", "/", "%")):
            for first in operators:
                for second in operators:
                    with self.subTest(first=first, second=second):
                        tree, _ = parse_expr(tokens_for(f"8 {first} 3 {second} 2"), 0)
                        self.assertEqual(shape(tree), binary(second, binary(first, eight, three), two))

    def test_parentheses_override_precedence_without_nodes(self):
        tokens = tokens_for("((a + 2)) * (3 - 1)")
        tree, end = parse_expr(tokens, 0)
        self.assertEqual(shape(tree), binary(
            "*", binary("+", leaf("Id a"), leaf("Int 2")),
            binary("-", leaf("Int 3"), leaf("Int 1")),
        ))
        self.assertEqual(end, len(tokens))

    def test_explicit_position_preserves_statement_delimiter(self):
        tokens = tokens_for("let x = a + 2;")
        before = tokens
        tree, end = parse_expr(tokens, 3)
        self.assertEqual(tree.label, "BinOp +")
        self.assertEqual(tokens[end].lexeme, ";")
        self.assertEqual(tokens, before)

    def test_all_relational_operators(self):
        for operator in ("==", "!=", "<", ">", "<=", ">="):
            with self.subTest(operator=operator):
                tokens = tokens_for(f"1 + 2 {operator} 3 * 4)")
                tree, end = parse_cond(tokens, 0)
                self.assertEqual(tree.label, f"RelOp {operator}")
                self.assertEqual(tuple(c.label for c in tree.children), ("BinOp +", "BinOp *"))
                self.assertEqual(tokens[end].lexeme, ")")

    def test_expression_error_locations_and_eof(self):
        with self.assertRaises(SyntaxIssue) as raised:
            parse_expr(tokens_for("1 +\n  )"), 0)
        self.assertEqual((raised.exception.line, raised.exception.column), (2, 3))
        for source in ("", "1 +", "(1 + 2"):
            with self.subTest(source=source):
                with self.assertRaises(SyntaxIssue) as raised:
                    parse_expr(tokens_for(source), 0)
                self.assertTrue(raised.exception.at_end_of_input)


class ASTDisplayTests(unittest.TestCase):
    def test_leaf_has_no_padding_or_trailing_newline(self):
        self.assertEqual(format_ast(ASTNode("Int 5")), "Int 5")

    def test_order_indentation_and_repeatability(self):
        tree = ASTNode("Program", (
            ASTNode("Print", (ASTNode("BinOp +", (ASTNode("Int 2"), ASTNode("Int 3"))),)),
            ASTNode("Print", (ASTNode("Id x"),)),
        ))
        expected = "Program\n  Print\n    BinOp +\n      Int 2\n      Int 3\n  Print\n    Id x"
        self.assertEqual(format_ast(tree), expected)
        self.assertEqual(format_ast(tree), expected)
        self.assertIsInstance(tree.children, tuple)


if __name__ == "__main__":
    unittest.main()
