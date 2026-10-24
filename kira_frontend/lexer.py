"""Lexer starter. Implement scanning here; keep parsing in parser.py."""
from .errors import LexicalIssue
from .tokens import Token


class Lexer:
    def lex(self, source: str) -> tuple[list[Token], list[LexicalIssue]]:
        """Return recognized tokens and every lexical issue in source order.

        TODO: track 1-based line/column positions; skip whitespace and # comments;
        recognize KIRA keywords, identifiers, integers, operators and delimiters;
        reject malformed identifiers such as digits immediately followed by letters.
        """
        raise NotImplementedError("Implement the KIRA lexer")
