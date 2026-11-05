"""Smoke checks for the incomplete scaffold, not compiler correctness tests."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StarterTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "kira.py"), *map(str, args)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    def test_help(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("source_file", result.stdout)

    def test_missing_file_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            result = self.run_cli(Path(folder) / "missing.kira")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_encoding_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            source = Path(folder) / "invalid.kira"
            source.write_bytes(b"\xff")
            result = self.run_cli(source)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_valid_program_prints_ast(self):
        result = self.run_cli(ROOT / "tests/public/public1_arithmetic_if.kira")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("\nAST\nProgram\n", result.stdout)
        self.assertIn("TOKEN STREAM", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_lexical_errors_skip_pending_parser_work(self):
        result = self.run_cli(ROOT / "tests/public/public4_lexical_errors.kira")
        self.assertEqual(result.returncode, 1)
        self.assertIn("LexicalError at line 4", result.stdout)
        self.assertIn("LexicalError at line 5", result.stdout)
        self.assertNotIn("Starter TODO", result.stderr)
        self.assertNotIn("\nAST", result.stdout)

    def test_six_public_inputs_have_expected_results(self):
        inputs = sorted((ROOT / "tests/public").glob("*.kira"))
        self.assertEqual(len(inputs), 6)
        for source in inputs:
            self.assertTrue(source.with_suffix(".expected.txt").is_file())


if __name__ == "__main__":
    unittest.main()
