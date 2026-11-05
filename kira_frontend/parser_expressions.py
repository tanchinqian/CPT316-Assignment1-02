"""Member 3 entry points for expression and condition parsing.

Implement with immutable AST nodes, explicit positions and functional style.
Shared peek/expect/error helpers are available in parser_support.py.
Sharrvesh's standalone reference harness lives in tests/parser_harness.py;
it is used only to verify the Member 2 port, never by the CLI.
"""
from .parser_support import ParseResult
from .tokens import Token


def parse_expr(tokens: tuple[Token, ...], position: int) -> ParseResult:
    """Parse arithmetic with precedence, left associativity and parentheses."""
    raise NotImplementedError("Implement Member 3 expression parsing")


def parse_cond(tokens: tuple[Token, ...], position: int) -> ParseResult:
    """Parse expr REL_OP expr and construct a RelOp node with two children."""
    raise NotImplementedError("Implement Member 3 condition parsing")
