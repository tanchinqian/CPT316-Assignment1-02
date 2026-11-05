"""Sharrvesh's standalone expression/display harness, adapted to shared types.

Source: CPT316- Sharrvesh.docx, section 1.1. This is test support for Member 2,
not Member 3's production implementation. Do not import it from kira_frontend.
"""
from typing import Tuple

from kira_frontend.ast_nodes import ASTNode
from kira_frontend.parser_support import ParseResult, expect, peek, raise_syntax_error
from kira_frontend.tokens import Token, TokenType


def parse_cond_stub(tokens: Tuple[Token, ...], pos: int) -> ParseResult:
    left_node, pos1 = parse_expr_stub(tokens, pos)
    rel_tok, pos2 = expect(tokens, pos1, TokenType.REL_OP)
    right_node, pos3 = parse_expr_stub(tokens, pos2)
    return ASTNode(f"RelOp {rel_tok.lexeme}", (left_node, right_node)), pos3

def parse_expr_stub(tokens: Tuple[Token, ...], pos: int) -> ParseResult:
    term_node, pos1 = parse_term_stub(tokens, pos)
    return parse_expr_tail_stub(tokens, pos1, term_node)

def parse_expr_tail_stub(tokens: Tuple[Token, ...], pos: int, left: ASTNode) -> ParseResult:
    tok = peek(tokens, pos)
    if tok is not None and tok.type == TokenType.ARITH_OP and tok.lexeme in ("+", "-"):
        _, pos1 = expect(tokens, pos, TokenType.ARITH_OP)
        right, pos2 = parse_term_stub(tokens, pos1)
        return parse_expr_tail_stub(tokens, pos2, ASTNode(f"BinOp {tok.lexeme}", (left, right)))
    return left, pos

def parse_term_stub(tokens: Tuple[Token, ...], pos: int) -> ParseResult:
    factor_node, pos1 = parse_factor_stub(tokens, pos)
    return parse_term_tail_stub(tokens, pos1, factor_node)

def parse_term_tail_stub(tokens: Tuple[Token, ...], pos: int, left: ASTNode) -> ParseResult:
    tok = peek(tokens, pos)
    if tok is not None and tok.type == TokenType.ARITH_OP and tok.lexeme in ("*", "/", "%"):
        _, pos1 = expect(tokens, pos, TokenType.ARITH_OP)
        right, pos2 = parse_factor_stub(tokens, pos1)
        return parse_term_tail_stub(tokens, pos2, ASTNode(f"BinOp {tok.lexeme}", (left, right)))
    return left, pos

def parse_factor_stub(tokens: Tuple[Token, ...], pos: int) -> ParseResult:
    tok = peek(tokens, pos)
    if tok is None:
        raise_syntax_error(tokens, pos, "expression")
    if tok.type == TokenType.IDENTIFIER:
        return ASTNode(f"Id {tok.lexeme}"), pos + 1
    if tok.type == TokenType.INTEGER:
        return ASTNode(f"Int {tok.lexeme}"), pos + 1
    if tok.type == TokenType.LPAREN:
        _, pos1 = expect(tokens, pos, TokenType.LPAREN, "(")
        expr_node, pos2 = parse_expr_stub(tokens, pos1)
        _, pos3 = expect(tokens, pos2, TokenType.RPAREN, ")")
        return expr_node, pos3
    raise_syntax_error(tokens, pos, "expression")

def format_ast(node: ASTNode, depth: int = 0) -> str:
    indent = "  " * depth
    child_lines = tuple(format_ast(child, depth + 1) for child in node.children)
    return "\n".join((f"{indent}{node.label}",) + child_lines)
