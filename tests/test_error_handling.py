"""Member 4 regression checks using the production compiler components."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import re
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import kira
from kira_frontend.lexer import Lexer
from kira_frontend.errors import LexicalIssue, SyntaxIssue
from kira_frontend.tokens import TokenType


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "tests" / "public"


class ErrorHandlingTests(unittest.TestCase):
    def test_redirected_output_escapes_unsupported_characters(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "case.kira"
            for source, status in (("print(1); \u03bb", 1), ("# \u03bb\nprint(1);", 0)):
                with self.subTest(source=source):
                    path.write_text(source, encoding="utf-8")
                    result = subprocess.run(
                        [sys.executable, str(ROOT / "kira.py"), str(path)],
                        capture_output=True, text=True, encoding="cp1252",
                        env=dict(os.environ, PYTHONIOENCODING="cp1252:strict"),
                        timeout=15,
                    )
                    self.assertEqual(result.returncode, status)
                    self.assertEqual(result.stderr, "")
                    self.assertIn(r"\u03bb", result.stdout)
                    self.assertNotIn("Traceback", result.stdout)
                    if status:
                        self.assertIn("LexicalError at line 1, col 11:", result.stdout)
                    else:
                        self.assertIn("\nAST\n", result.stdout)

    def test_issue_message_contracts(self):
        self.assertEqual(str(LexicalIssue(2, 11, "invalid character '$'")),
                         "LexicalError at line 2, col 11: invalid character '$'")
        self.assertEqual(str(SyntaxIssue("expected ')' before ';'", 1, 19)),
                         "SyntaxError at line 1, col 19: expected ')' before ';'")
        self.assertEqual(str(SyntaxIssue("expected '}'", at_end_of_input=True)),
                         "SyntaxError at end of input: expected '}'")

    def run_source(self, source):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "case.kira"
            path.write_text(source, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(ROOT / "kira.py"), str(path)],
                capture_output=True, text=True, check=False, timeout=15,
            )

    def test_lexer_reports_all_issues_and_resumes_at_valid_tokens(self):
        tokens, issues = Lexer().lex("$ 9lives @ !\nprint(1);")
        self.assertEqual([(e.line, e.column) for e in issues],
                         [(1, 1), (1, 3), (1, 10), (1, 12)])
        self.assertEqual([t.lexeme for t in tokens], ["print", "(", "1", ")", ";"])
        self.assertEqual(str(issues[1]),
                         "LexicalError at line 1, col 3: malformed token '9lives'")

    def test_comments_and_newlines_preserve_error_positions(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                tokens, issues = Lexer().lex("# $ @ ! 9lives" + newline + "\t@" + newline + "print(1);")
                self.assertEqual([(e.line, e.column) for e in issues], [(2, 2)])
                self.assertEqual((tokens[0].line, tokens[0].column), (3, 1))

    def test_lexical_failure_never_calls_parser_or_formatter(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "case.kira"
            path.write_text("$ print(;")
            output = StringIO()
            with patch.object(sys, "argv", ["kira.py", str(path)]), redirect_stdout(output), \
                    patch.object(kira, "parse_program") as parser, \
                    patch.object(kira, "format_ast") as formatter:
                self.assertEqual(kira.main(), 1)
            parser.assert_not_called()
            formatter.assert_not_called()
        self.assertIn("Parsing skipped.", output.getvalue())
        self.assertNotIn("SyntaxError", output.getvalue())

    def test_only_first_syntax_error_is_printed(self):
        result = self.run_source("print(;\nlet = ;")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count("SyntaxError"), 1)
        self.assertIn("SyntaxError at line 1, col 7: expected expression before ';'", result.stdout)
        self.assertNotIn("\nAST\n", result.stdout)

    def test_empty_and_truncated_sources_report_eof(self):
        for source, expected in (
            ("", "declaration or statement"),
            ("# comment only", "declaration or statement"),
            ("let x =", "expression"),
            ("print(1)", "';'"),
            ("while(x<1){print(x);", "'}'"),
        ):
            with self.subTest(source=source):
                result = self.run_source(source)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertIn(f"SyntaxError at end of input: expected {expected}", result.stdout)
                self.assertNotIn("\nAST\n", result.stdout)

    def test_no_semantic_checks_or_evaluation(self):
        result = self.run_source("print(unknown / 0);")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("BinOp /", result.stdout)

    def test_lexical_boundaries(self):
        for source, messages in (
            ("9lives 12abc_3 4_name", ["malformed token '9lives'", "malformed token '12abc_3'", "malformed token '4_name'"]),
            ("! !=", ["invalid character '!'"]),
            ("_name", ["invalid character '_'"]),
            ("1.5", ["invalid character '.'"]),
        ):
            with self.subTest(source=source):
                _, issues = Lexer().lex(source)
                self.assertEqual([issue.message for issue in issues], messages)
                result = self.run_source(source)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertEqual(result.stdout.count("LexicalError"), len(messages))
                self.assertNotIn("SyntaxError", result.stdout)

    def test_invalid_grammar_reports_offending_token(self):
        for source, column, message in (
            ("let x 1;", 7, "expected '='"),
            ("let if = 1;", 5, "expected identifier"),
            ("print(1;", 8, "expected ')'"),
            ("print(1) print(2);", 10, "expected ';'"),
            ("print(-1);", 7, "expected expression"),
            ("if(x){print(1);}", 5, "expected rel_op"),
            ("if(x<){print(1);}", 6, "expected expression"),
            ("while(x<1){}", 12, "empty block"),
            ("while(x<1){let a=1;}", 12, "declarations"),
            ("else{print(1);}", 1, "expected statement"),
            ("print(1);}", 10, "expected statement"),
        ):
            with self.subTest(source=source):
                result = self.run_source(source)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertIn(f"SyntaxError at line 1, col {column}: {message}", result.stdout)
                self.assertEqual(result.stdout.count("SyntaxError"), 1)
                self.assertNotIn("\nAST\n", result.stdout)

    def test_recursion_limit_has_no_traceback_or_partial_ast(self):
        for source in ("print(1);\n" * 1500,
                       "print(" + "(" * 1500 + "1" + ")" * 1500 + ");"):
            with self.subTest(kind=source[:30]):
                result = self.run_source(source)
                self.assertEqual(result.returncode, 2)
                self.assertIn("KIRA implementation limit:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertNotIn("\nAST\n", result.stdout)

    def test_formatter_recursion_is_also_handled(self):
        output, errors = StringIO(), StringIO()
        with patch.object(sys, "argv", ["kira.py", str(PUBLIC / "public1_arithmetic_if.kira")]), \
                redirect_stdout(output), redirect_stderr(errors), \
                patch.object(kira, "format_ast", side_effect=RecursionError):
            self.assertEqual(kira.main(), 2)
        self.assertIn("implementation limit", errors.getvalue())
        self.assertNotIn("\nAST\n", output.getvalue())

    def test_all_public_outputs_against_official_expectations(self):
        for path in sorted(PUBLIC.glob("*.kira")):
            with self.subTest(program=path.name):
                expected = path.with_suffix(".expected.txt").read_text()
                result = self.run_source(path.read_text())
                self.assertEqual(result.stderr, "")
                count_section = expected.split("== TOKEN COUNTS ==\n")[1].split("\n\n")[0]
                total = int(re.search(r"Total tokens: (\d+)", count_section)[1])
                counts = dict(re.findall(r"^  ([A-Z_]+)\s+(\d+)$", count_section, re.M))
                actual_section = result.stdout.split("\nTOKEN COUNTS\n")[1]
                actual = dict(re.findall(r"^\|\s*([A-Z_]+)\s*\|\s*(\d+)\s*\|$", actual_section, re.M))
                self.assertEqual(int(actual["TOTAL"]), total)
                for token_type in TokenType:
                    self.assertEqual(int(actual[token_type.value]), int(counts.get(token_type.value, 0)))
                expected_errors = re.findall(r"^(?:LexicalError|SyntaxError).*$", expected, re.M)
                actual_errors = re.findall(r"^(?:LexicalError|SyntaxError).*$", result.stdout, re.M)
                self.assertEqual(actual_errors, expected_errors)
                self.assertEqual(result.returncode, 1 if expected_errors else 0)
                self.assertEqual(int(actual["INVALID"]), sum(e.startswith("LexicalError") for e in expected_errors))
                if expected_errors:
                    self.assertNotIn("\nAST\n", result.stdout)
                else:
                    self.assertEqual(result.stdout.split("\nAST\n")[1].rstrip("\n"),
                                     expected.split("== AST ==\n")[1].rstrip("\n"))


if __name__ == "__main__":
    unittest.main()
