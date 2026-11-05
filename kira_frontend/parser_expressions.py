"""Functional expression/condition parser adapted from Sharrvesh's reference harness.

Each function returns an immutable AST and the next token position. No parser
cursor or token stream is mutated. The original reference remains in tests.
"""
from .ast_nodes import ASTNode
from .parser_support import ParseResult, expect, peek, raise_syntax_error
from .tokens import Token, TokenType


def parse_cond(tokens: tuple[Token, ...], position: int) -> ParseResult:
    """Parse expr REL_OP expr; leave the enclosing closing parenthesis."""
    left_node, position1 = parse_expr(tokens, position)
    rel_tok, position2 = expect(tokens, position1, TokenType.REL_OP)
    right_node, position3 = parse_expr(tokens, position2)
    return ASTNode(f"RelOp {rel_tok.lexeme}", (left_node, right_node)), position3

def parse_expr(tokens: tuple[Token, ...], position: int) -> ParseResult:
    """Parse addition/subtraction after higher-precedence terms."""
    term_node, position1 = parse_term(tokens, position)
    return parse_expr_tail(tokens, position1, term_node)

def parse_expr_tail(tokens: tuple[Token, ...], position: int, left: ASTNode) -> ParseResult:
    # Carry the completed left subtree forward to preserve left associativity.
    tok = peek(tokens, position)
    if tok is not None and tok.type == TokenType.ARITH_OP and tok.lexeme in ("+", "-"):
        _, position1 = expect(tokens, position, TokenType.ARITH_OP)
        right, position2 = parse_term(tokens, position1)
        return parse_expr_tail(tokens, position2, ASTNode(f"BinOp {tok.lexeme}", (left, right)))
    return left, position

def parse_term(tokens: tuple[Token, ...], position: int) -> ParseResult:
    """Parse multiplication, division and remainder before addition/subtraction."""
    factor_node, position1 = parse_factor(tokens, position)
    return parse_term_tail(tokens, position1, factor_node)

def parse_term_tail(tokens: tuple[Token, ...], position: int, left: ASTNode) -> ParseResult:
    # Carry the completed left subtree forward to preserve left associativity.
    tok = peek(tokens, position)
    if tok is not None and tok.type == TokenType.ARITH_OP and tok.lexeme in ("*", "/", "%"):
        _, position1 = expect(tokens, position, TokenType.ARITH_OP)
        right, position2 = parse_factor(tokens, position1)
        return parse_term_tail(tokens, position2, ASTNode(f"BinOp {tok.lexeme}", (left, right)))
    return left, position

def parse_factor(tokens: tuple[Token, ...], position: int) -> ParseResult:
    """Parse a leaf or parenthesized expression; unary operators are invalid."""
    tok = peek(tokens, position)
    if tok is None:
        raise_syntax_error(tokens, position, "expression")
    if tok.type == TokenType.IDENTIFIER:
        return ASTNode(f"Id {tok.lexeme}"), position + 1
    if tok.type == TokenType.INTEGER:
        return ASTNode(f"Int {tok.lexeme}"), position + 1
    if tok.type == TokenType.LPAREN:
        _, position1 = expect(tokens, position, TokenType.LPAREN, "(")
        expr_node, position2 = parse_expr(tokens, position1)
        _, position3 = expect(tokens, position2, TokenType.RPAREN, ")")
        return expr_node, position3
    raise_syntax_error(tokens, position, "expression")
