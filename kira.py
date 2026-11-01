"""Command-line starter for the KIRA compiler front end."""
import argparse
from collections import Counter
from pathlib import Path
import sys

from kira_frontend.ast_nodes import format_ast
from kira_frontend.errors import SyntaxIssue
from kira_frontend.lexer import Lexer
from kira_frontend.parser import parse_program
from kira_frontend.tokens import TokenType


def print_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    widths = [
        max([len(header), *(len(row[index]) for row in rows)])
        for index, header in enumerate(headers)
    ]
    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    def print_row(values: tuple[str, ...]) -> None:
        print("| " + " | ".join(value.ljust(width) for value, width in zip(values, widths)) + " |")

    print(border)
    print_row(headers)
    print(border)
    for row in rows:
        print_row(row)
    print(border)


def main() -> int:
    cli = argparse.ArgumentParser(description="Lex and parse a KIRA source file")
    cli.add_argument("source_file", type=Path, help="path to a .kira file")
    args = cli.parse_args()
    try:
        source = args.source_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        cli.error(str(error))

    tokens, lexical_issues = Lexer().lex(source)
    print("KIRA SOURCE")
    print(source.rstrip("\r\n"))
    print()
    print("TOKEN STREAM")
    token_rows = [
        (str(token.line), str(token.column), token.type.value, repr(token.lexeme))
        for token in tokens
    ]
    print_table(("LINE", "COLUMN", "TYPE", "LEXEME"), token_rows)

    print("\nTOKEN COUNTS")
    counts = Counter(token.type.value for token in tokens)
    count_rows = [(name, str(counts[name.value])) for name in TokenType]
    count_rows.insert(0, ("TOTAL", str(len(tokens))))
    print_table(("TOKEN TYPE", "COUNT"), count_rows)

    if lexical_issues:
        print("\n" + "=" * 24)
        print("LEXICAL ERRORS")
        print("=" * 24)
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
