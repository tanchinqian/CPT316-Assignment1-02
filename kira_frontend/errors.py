"""Structured lexical and syntax issues for consistent CLI output."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LexicalIssue:
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"LexicalError at line {self.line}, col {self.column}: {self.message}"


@dataclass(frozen=True)
class SyntaxIssue(Exception):
    message: str
    line: int | None = None
    column: int | None = None
    at_end_of_input: bool = False

    def __str__(self) -> str:
        if self.at_end_of_input:
            return f"SyntaxError at end of input: {self.message}"
        return f"SyntaxError at line {self.line}, col {self.column}: {self.message}"
