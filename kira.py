"""Command-line starter for the KIRA compiler front end."""
import argparse
from collections import Counter
from pathlib import Path
import sys

from kira_frontend.ast_nodes import format_ast
from kira_frontend.errors import SyntaxIssue
from kira_frontend.lexer import Lexer
from kira_frontend.parser import parse_program


def main() -> int:
    cli = argparse.ArgumentParser(description="Lex and parse a KIRA source file")
    cli.add_argument("source_file", type=Path, help="path to a .kira file")
    args = cli.parse_args()
    try:
        source = args.source_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        cli.error(str(error))

    tokens, lexical_issues = Lexer().lex(source)
    print("Token stream")
    for token in tokens:
        print(f"{token.type.value} {token.lexeme!r} at line {token.line}, col {token.column}")
    print("\nToken counts")
    counts = Counter(token.type.value for token in tokens)
    print(f"TOTAL: {len(tokens)}")
    for name, count in sorted(counts.items()):
        print(f"{name}: {count}")

    if lexical_issues:
        for issue in lexical_issues:
            print(issue)
        return 1  # Required: do not run the parser after lexical errors.
    try:
        tree, _next_position = parse_program(tuple(tokens))
    except SyntaxIssue as issue:
        print(issue)
        return 1
    print("\nAST")
    print(format_ast(tree))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except NotImplementedError as error:
        print(f"Starter TODO: {error}", file=sys.stderr)
        raise SystemExit(2)
