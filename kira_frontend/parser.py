"""Statement/block parser ported from Sharrvesh's Member 2 deliverable.

Repository integration uses the shared Token, ASTNode and SyntaxIssue types.
Expression and condition callbacks belong to Member 3; tests inject the
standalone harness supplied in Sharrvesh's document.
"""
from typing import Tuple

from . import parser_expressions
from .ast_nodes import ASTNode
from .errors import SyntaxIssue
from .parser_support import (
    ExprParserFn, ParseListResult, ParseResult, expect, peek, raise_syntax_error,
)
from .tokens import Token, TokenType


def parse_program(
    tokens: Tuple[Token, ...],
    position: int = 0,
    *,
    parse_expr: ExprParserFn | None = None,
    parse_cond: ExprParserFn | None = None,
) -> ParseResult:
    """Parse a nonempty program and return its tree and consumed position.

    The CLI uses Member 3's default expression/condition entry points.
    Explicit callbacks allow independent testing of the statement parser.
    All tokens from position onward must be consumed; there is no EOF token.
    """
    if not 0 <= position <= len(tokens):
        raise ValueError("position must be between 0 and len(tokens)")
    if position == len(tokens):
        raise SyntaxIssue("expected declaration or statement", at_end_of_input=True)
    expr = parser_expressions.parse_expr if parse_expr is None else parse_expr
    cond = parser_expressions.parse_cond if parse_cond is None else parse_cond
    items, next_pos = parse_item_list(tokens, position, expr, cond)
    if next_pos != len(tokens):
        raise_syntax_error(tokens, next_pos, "end of input")
    return ASTNode("Program", items), next_pos


def parse_item_list(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseListResult:
    """
    Transformed Grammar:
    <item_list>      -> <item> <item_list_tail>
    <item_list_tail> -> <item> <item_list_tail> | ε
    """
    first_item, next_pos = parse_item(tokens, pos, parse_expr, parse_cond)
    rest_items, final_pos = parse_item_list_tail(tokens, next_pos, parse_expr, parse_cond)
    return (first_item,) + rest_items, final_pos


def parse_item_list_tail(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseListResult:
    """Recursively parses remaining top-level items until end of token stream."""
    if pos >= len(tokens):
        return (), pos
    next_item, next_pos = parse_item(tokens, pos, parse_expr, parse_cond)
    rest_items, final_pos = parse_item_list_tail(tokens, next_pos, parse_expr, parse_cond)
    return (next_item,) + rest_items, final_pos


def parse_item(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseResult:
    """
    Grammar: <item> -> <decl> | <stmt>
    Allows 'let' declarations only at the top level of the program.
    """
    tok = peek(tokens, pos)
    if tok is not None and tok.type == TokenType.KEYWORD and tok.lexeme == "let":
        return parse_decl(tokens, pos, parse_expr)
    return parse_stmt(tokens, pos, parse_expr, parse_cond)


def parse_decl(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn
) -> ParseResult:
    """
    Grammar: <decl> -> 'let' id '=' <expr> ';'
    AST Node: 'Let <id>' with child: (expr_node,)
    """
    _, pos1 = expect(tokens, pos, TokenType.KEYWORD, "let")
    id_tok, pos2 = expect(tokens, pos1, TokenType.IDENTIFIER)
    _, pos3 = expect(tokens, pos2, TokenType.ASSIGN, "=")
    expr_node, pos4 = parse_expr(tokens, pos3)
    _, pos5 = expect(tokens, pos4, TokenType.SEMICOLON, ";")
    return ASTNode(f"Let {id_tok.lexeme}", (expr_node,)), pos5


def parse_stmt(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseResult:
    """
    Grammar: <stmt> -> <assign> | <if_stmt> | <while_stmt> | <print_stmt>
    Rejects 'let' declarations inside blocks with a clear SyntaxError.
    """
    tok = peek(tokens, pos)
    if tok is None:
        raise_syntax_error(tokens, pos, "statement")

    if tok.type == TokenType.KEYWORD:
        if tok.lexeme == "let":
            raise SyntaxIssue(
                "declarations ('let') are not allowed inside a block",
                tok.line,
                tok.column
            )
        if tok.lexeme == "if":
            return parse_if_stmt(tokens, pos, parse_expr, parse_cond)
        if tok.lexeme == "while":
            return parse_while_stmt(tokens, pos, parse_expr, parse_cond)
        if tok.lexeme == "print":
            return parse_print_stmt(tokens, pos, parse_expr)

    if tok.type == TokenType.IDENTIFIER:
        return parse_assign(tokens, pos, parse_expr)

    raise SyntaxIssue(
        f"expected statement before '{tok.lexeme}'",
        tok.line,
        tok.column
    )


def parse_assign(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn
) -> ParseResult:
    """
    Grammar: <assign> -> id '=' <expr> ';'
    AST Node: 'Assign <id>' with child: (expr_node,)
    """
    id_tok, pos1 = expect(tokens, pos, TokenType.IDENTIFIER)
    _, pos2 = expect(tokens, pos1, TokenType.ASSIGN, "=")
    expr_node, pos3 = parse_expr(tokens, pos2)
    _, pos4 = expect(tokens, pos3, TokenType.SEMICOLON, ";")
    return ASTNode(f"Assign {id_tok.lexeme}", (expr_node,)), pos4


def parse_if_stmt(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseResult:
    """
    Transformed Grammar:
    <if_stmt>   -> 'if' '(' <cond> ')' <block> <else_part>
    <else_part> -> 'else' <block> | ε
    AST Node: 'If' with children: (cond_node, Then_block [, Else_block])
    """
    _, pos1 = expect(tokens, pos, TokenType.KEYWORD, "if")
    _, pos2 = expect(tokens, pos1, TokenType.LPAREN, "(")
    cond_node, pos3 = parse_cond(tokens, pos2)
    _, pos4 = expect(tokens, pos3, TokenType.RPAREN, ")")
    then_block, pos5 = parse_block(tokens, pos4, "Then", parse_expr, parse_cond)

    tok = peek(tokens, pos5)
    if tok is not None and tok.type == TokenType.KEYWORD and tok.lexeme == "else":
        _, pos6 = expect(tokens, pos5, TokenType.KEYWORD, "else")
        else_block, pos7 = parse_block(tokens, pos6, "Else", parse_expr, parse_cond)
        return ASTNode("If", (cond_node, then_block, else_block)), pos7

    return ASTNode("If", (cond_node, then_block)), pos5


def parse_while_stmt(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseResult:
    """
    Grammar: <while_stmt> -> 'while' '(' <cond> ')' <block>
    AST Node: 'While' with children: (cond_node, Body_block)
    """
    _, pos1 = expect(tokens, pos, TokenType.KEYWORD, "while")
    _, pos2 = expect(tokens, pos1, TokenType.LPAREN, "(")
    cond_node, pos3 = parse_cond(tokens, pos2)
    _, pos4 = expect(tokens, pos3, TokenType.RPAREN, ")")
    body_block, pos5 = parse_block(tokens, pos4, "Body", parse_expr, parse_cond)
    return ASTNode("While", (cond_node, body_block)), pos5


def parse_print_stmt(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn
) -> ParseResult:
    """
    Grammar: <print_stmt> -> 'print' '(' <expr> ')' ';'
    AST Node: 'Print' with child: (expr_node,)
    """
    _, pos1 = expect(tokens, pos, TokenType.KEYWORD, "print")
    _, pos2 = expect(tokens, pos1, TokenType.LPAREN, "(")
    expr_node, pos3 = parse_expr(tokens, pos2)
    _, pos4 = expect(tokens, pos3, TokenType.RPAREN, ")")
    _, pos5 = expect(tokens, pos4, TokenType.SEMICOLON, ";")
    return ASTNode("Print", (expr_node,)), pos5


def parse_block(
    tokens: Tuple[Token, ...],
    pos: int,
    block_label: str,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseResult:
    """
    Grammar: <block> -> '{' <stmt_list> '}'
    Enforces that blocks contain at least one statement and assigns the
    contextual AST label ('Then', 'Else', or 'Body').
    """
    _, pos1 = expect(tokens, pos, TokenType.LBRACE, "{")
    tok = peek(tokens, pos1)
    if tok is not None and tok.type == TokenType.RBRACE:
        raise SyntaxIssue(
            "empty block is not allowed; expected statement before '}'",
            tok.line,
            tok.column
        )
    stmts, pos2 = parse_stmt_list(tokens, pos1, parse_expr, parse_cond)
    _, pos3 = expect(tokens, pos2, TokenType.RBRACE, "}")
    return ASTNode(block_label, stmts), pos3


def parse_stmt_list(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseListResult:
    """
    Transformed Grammar:
    <stmt_list>      -> <stmt> <stmt_list_tail>
    <stmt_list_tail> -> <stmt> <stmt_list_tail> | ε
    """
    first_stmt, next_pos = parse_stmt(tokens, pos, parse_expr, parse_cond)
    rest_stmts, final_pos = parse_stmt_list_tail(tokens, next_pos, parse_expr, parse_cond)
    return (first_stmt,) + rest_stmts, final_pos


def parse_stmt_list_tail(
    tokens: Tuple[Token, ...],
    pos: int,
    parse_expr: ExprParserFn,
    parse_cond: ExprParserFn
) -> ParseListResult:
    """
    Recursively parses statements inside a block until '}' or end of input.
    Returning cleanly on None allows parse_block to report:
    'SyntaxError at end of input: expected '}' '
    """
    tok = peek(tokens, pos)
    if tok is None or tok.type == TokenType.RBRACE:
        return (), pos
    next_stmt, next_pos = parse_stmt(tokens, pos, parse_expr, parse_cond)
    rest_stmts, final_pos = parse_stmt_list_tail(tokens, next_pos, parse_expr, parse_cond)
    return (next_stmt,) + rest_stmts, final_pos
