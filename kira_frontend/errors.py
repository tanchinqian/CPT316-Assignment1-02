"""Structured lexical and syntax issues for consistent CLI output."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LexicalIssue:
    """One recoverable scanning issue, located at its 1-based start position.

    The lexer collects these records so scanning can report every issue.
    """
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"LexicalError at line {self.line}, col {self.column}: {self.message}"


@dataclass(frozen=True)
class SyntaxIssue(Exception):
    """First parsing failure; raising it unwinds parsing without a partial AST.

    Token errors supply 1-based line and column values. EOF errors instead set
    at_end_of_input=True and leave both coordinates unset, because no offending
    token exists. Rendering stays here; printing belongs to the CLI.
    """
    message: str
    line: int | None = None
    column: int | None = None
    at_end_of_input: bool = False

    def __str__(self) -> str:
        if self.at_end_of_input:
            return f"SyntaxError at end of input: {self.message}"
        return f"SyntaxError at line {self.line}, col {self.column}: {self.message}"
