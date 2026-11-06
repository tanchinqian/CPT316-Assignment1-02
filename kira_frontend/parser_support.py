"""Shared parser helpers adapted from Sharrvesh's Member 2 deliverable."""
from typing import Callable, NoReturn, Optional, Tuple

from .ast_nodes import ASTNode
from .errors import SyntaxIssue
from .tokens import Token, TokenType


ParseResult = Tuple[ASTNode, int]
ParseListResult = Tuple[Tuple[ASTNode, ...], int]
ExprParserFn = Callable[[Tuple[Token, ...], int], ParseResult]


def peek(tokens: Tuple[Token, ...], pos: int) -> Optional[Token]:
    """Pure function to inspect the current token without mutating state."""
    return tokens[pos] if pos < len(tokens) else None


def raise_syntax_error(tokens: Tuple[Token, ...], pos: int, expected_desc: str) -> NoReturn:
    """Raises a SyntaxIssue at the current token or at end of input."""
    tok = peek(tokens, pos)
    if tok is None:
        raise SyntaxIssue(f"expected {expected_desc}", at_end_of_input=True)
    raise SyntaxIssue(
        f"expected {expected_desc} before '{tok.lexeme}'",
        tok.line,
        tok.column
    )


def expect(
    tokens: Tuple[Token, ...],
    pos: int,
    expected_type: TokenType,
    expected_lexeme: Optional[str] = None
) -> Tuple[Token, int]:
    """
    Pure function that verifies tokens[pos] matches expected_type (and optional lexeme).
    Returns (matched_token, pos + 1) without mutating any state in place.
    """
    tok = peek(tokens, pos)
    desc = f"'{expected_lexeme}'" if expected_lexeme else expected_type.value.lower()
    if tok is None or tok.type != expected_type or (expected_lexeme is not None and tok.lexeme != expected_lexeme):
        raise_syntax_error(tokens, pos, desc)
    return tok, pos + 1
