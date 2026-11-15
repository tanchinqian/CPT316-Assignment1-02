"""Immutable AST record and functional text-tree display."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ASTNode:
    """Generic immutable node; use labels/children required by the KIRA brief."""
    label: str
    children: tuple["ASTNode", ...] = ()


def format_ast(root: ASTNode) -> str:
    return _format_ast(root, 0)


def _format_ast(node: ASTNode, depth: int) -> str:
    child_lines = tuple(map(lambda child: _format_ast(child, depth + 1), node.children))
    return "\n".join(("  " * depth + node.label,) + child_lines)
