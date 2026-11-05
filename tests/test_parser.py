"""Member 2 integration checks using Sharrvesh's Member 3 reference harness."""
from contextlib import redirect_stdout
from dataclasses import FrozenInstanceError
from io import StringIO
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import kira
from kira_frontend import parser_expressions
from kira_frontend.ast_nodes import ASTNode
from kira_frontend.errors import SyntaxIssue
from kira_frontend.lexer import Lexer
from kira_frontend.parser import parse_program
from parser_harness import format_ast, parse_cond_stub, parse_expr_stub


PUBLIC = Path(__file__).resolve().parent / "public"


def parse(source, position=0):
    tokens, issues = Lexer().lex(source)
    if issues:
        raise AssertionError(issues)
    return parse_program(
        tuple(tokens), position,
        parse_expr=parse_expr_stub, parse_cond=parse_cond_stub,
    )


class StatementParserTests(unittest.TestCase):
    def test_public_valid_programs_match_exact_trees(self):
        for path in sorted(PUBLIC.glob("public[123]_*.kira")):
            with self.subTest(program=path.name):
                tokens, issues = Lexer().lex(path.read_text())
                self.assertFalse(issues)
                before = tuple(tokens)
                tree, end = parse_program(
                    before, parse_expr=parse_expr_stub, parse_cond=parse_cond_stub,
                )
                self.assertEqual(end, len(before))
                self.assertEqual(tuple(tokens), before)
                self.assertIsInstance(tree, ASTNode)
                expected = path.with_suffix(".expected.txt").read_text()
                self.assertEqual(format_ast(tree), expected.split("== AST ==\n")[1].strip())

    def test_public_syntax_errors_use_shared_exception(self):
        for name, line, column, eof in (
            ("public5_syntax_error.kira", 3, 19, False),
            ("public6_syntax_end_of_input.kira", None, None, True),
        ):
            with self.subTest(program=name):
                with self.assertRaises(SyntaxIssue) as raised:
                    parse((PUBLIC / name).read_text())
                error = raised.exception
                self.assertEqual((error.line, error.column), (line, column))
                self.assertEqual(error.at_end_of_input, eof)

    def test_invalid_statement_and_block_forms(self):
        cases = (
            ("", "end of input"),
            ("# only comment", "end of input"),
            ("if (x < 1) {}", "empty block"),
            ("if (x < 1) { print(x); } else {}", "empty block"),
            ("while (x < 1) {}", "empty block"),
            ("while (x < 1) { let a = 1; }", "declarations"),
            ("if (x < 1) { print(x); } else { let a = 1; }", "declarations"),
            ("if (x < 1) print(x);", "expected '{'"),
            ("else { print(1); }", "expected statement"),
            ("{ print(1); }", "expected statement"),
            ("print(1); }", "expected statement"),
            ("let if = 1;", "expected identifier"),
            ("let x == 1;", "expected '='"),
            ("print(1)", "expected ';'"),
            ("x = 1", "expected ';'"),
            ("if (x < 1) { print(x);", "expected '}'"),
            ("if (x < 1) { print(x); } else", "expected '{'"),
            ("print(-1);", "expected expression"),
        )
        for source, message in cases:
            with self.subTest(source=source):
                with self.assertRaises(SyntaxIssue) as raised:
                    parse(source)
                self.assertIn(message, str(raised.exception))

    def test_first_error_preserves_line_and_column(self):
        with self.assertRaises(SyntaxIssue) as raised:
            parse("print(1);\n  print(2;\nlet = 3;")
        self.assertEqual((raised.exception.line, raised.exception.column), (2, 10))

    def test_optional_else_and_nested_control_flow(self):
        tree, _ = parse("if (x < 1) { while (x < 2) { x = x + 1; } } print(x);")
        conditional, following = tree.children
        self.assertEqual(len(conditional.children), 2)
        then = conditional.children[1]
        self.assertEqual(then.label, "Then")
        loop = then.children[0]
        self.assertEqual(loop.label, "While")
        self.assertEqual(loop.children[1].label, "Body")
        self.assertEqual(following.label, "Print")

    def test_declaration_after_statement_and_undeclared_identifier(self):
        tree, _ = parse("print(unknown); let x = 1; x = 2;")
        self.assertEqual(tuple(n.label for n in tree.children), ("Print", "Let x", "Assign x"))
        self.assertIsInstance(tree.children, tuple)
        with self.assertRaises(FrozenInstanceError):
            tree.label = "Changed"

    def test_explicit_start_position(self):
        tree, end = parse("print(0); let x = 1;", position=5)
        self.assertEqual(tuple(n.label for n in tree.children), ("Let x",))
        self.assertEqual(end, 10)
        with self.assertRaises(SyntaxIssue) as raised:
            parse("print(0);", position=5)
        self.assertTrue(raised.exception.at_end_of_input)

    def test_cli_with_reference_member3_callbacks(self):
        # These injections exercise the real CLI/lexer/parser integration without
        # promoting the reference harness into Member 3's production component.
        for path in sorted(PUBLIC.glob("*.kira")):
            with self.subTest(program=path.name):
                output = StringIO()
                with (
                    patch.object(parser_expressions, "parse_expr", parse_expr_stub),
                    patch.object(parser_expressions, "parse_cond", parse_cond_stub),
                    patch.object(kira, "format_ast", format_ast),
                    patch("sys.argv", ["kira.py", str(path)]),
                    redirect_stdout(output),
                ):
                    code = kira.main()
                actual = output.getvalue()
                expected = path.with_suffix(".expected.txt").read_text()
                self.assertLess(actual.index("TOKEN STREAM"), actual.index("TOKEN COUNTS"))
                if not re.search(r"(?:Lexical|Syntax)Error at", expected):
                    self.assertEqual(code, 0)
                    self.assertEqual(actual.split("\nAST\n")[1].strip(), expected.split("== AST ==\n")[1].strip())
                else:
                    self.assertEqual(code, 1)
                    self.assertNotIn("\nAST\n", actual)
                    for location in re.findall(r"(?:Lexical|Syntax)Error at (?:line \d+|end of input)", expected):
                        self.assertIn(location, actual)

    def test_cli_never_calls_parser_after_lexical_errors(self):
        with (
            patch.object(kira, "parse_program") as parser,
            patch("sys.argv", ["kira.py", str(PUBLIC / "public4_lexical_errors.kira")]),
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(kira.main(), 1)
        parser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
