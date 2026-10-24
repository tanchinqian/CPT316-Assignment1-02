"""KIRA token definitions. Keep kinds aligned with the current assignment brief."""
from dataclasses import dataclass
from enum import Enum


class TokenType(str, Enum):
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    ARITH_OP = "ARITH_OP"
    REL_OP = "REL_OP"
    ASSIGN = "ASSIGN"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"


@dataclass(frozen=True)
class Token:
    """A token with 1-based source line and column positions."""
    type: TokenType
    lexeme: str
    line: int
    column: int
