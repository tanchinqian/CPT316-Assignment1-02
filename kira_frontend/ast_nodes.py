"""Immutable AST record and required text-tree display interface."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ASTNode:
    """Generic immutable node; use labels/children required by the KIRA brief."""
    label: str
    children: tuple["ASTNode", ...] = ()


def format_ast(root: ASTNode) -> str:
    """TODO: one node per line, two spaces per level, exact required labels."""
    raise NotImplementedError("Implement the required indented AST display")
