"""Render the existing immutable AST as a standalone SVG, using only Python."""
from html import escape
from itertools import accumulate

from .ast_nodes import ASTNode


def format_ast_svg(root: ASTNode) -> str:
    """Return a scalable tree diagram without changing the AST or writing files."""
    width, height, drawing = _draw_tree(root)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + 48}" '
        f'height="{height + 48}" viewBox="0 0 {width + 48} {height + 48}" '
        'role="img" aria-label="KIRA abstract syntax tree">'
        '<title>KIRA abstract syntax tree</title>'
        '<rect width="100%" height="100%" fill="white"/>'
        f'<g transform="translate(24,24)">{drawing}</g></svg>'
    )


def _draw_tree(node: ASTNode) -> tuple[int, int, str]:
    """Give each child its own width so sibling subtrees cannot overlap."""
    children = tuple(map(_draw_tree, node.children))
    box_width = max(112, len(node.label) * 10 + 36)
    gap, level, box_height = 28, 112, 44
    children_width = sum(child[0] for child in children) + gap * max(0, len(children) - 1)
    width = max(box_width, children_width)
    height = box_height + (level + max(c[1] for c in children) - box_height if children else 0)
    offsets = tuple(accumulate((0,) + tuple(c[0] + gap for c in children)))
    left = (width - children_width) / 2

    def draw_child(pair: tuple[tuple[int, int, str], int]) -> str:
        child, offset = pair
        x = left + offset
        child_center = x + child[0] / 2
        return (
            f'<path d="M {width / 2} {box_height} '
            f'C {width / 2} 78, {child_center} 78, {child_center} {level}" '
            'fill="none" stroke="#8296aa" stroke-width="2"/>'
            f'<g transform="translate({x},{level})">{child[2]}</g>'
        )

    branches = ''.join(map(draw_child, zip(children, offsets)))
    fill, stroke, text = ('#173e60', '#173e60', '#ffffff') if node.label == 'Program' else (
        ('#eef7f1', '#75a486', '#244c35') if not children else
        ('#edf4fa', '#7295b5', '#173e60')
    )
    box = (
        f'<rect x="{(width - box_width) / 2}" width="{box_width}" height="{box_height}" '
        f'rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<text x="{width / 2}" y="28" text-anchor="middle" '
        f'font-family="Consolas, monospace" font-size="16" font-weight="600" '
        f'fill="{text}">{escape(node.label)}</text>'
    )
    return width, height, branches + box
