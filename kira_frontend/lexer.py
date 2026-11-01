"""Lexer starter. Implement scanning here; keep parsing in parser.py."""
from .errors import LexicalIssue
from .tokens import Token, TokenType


KEYWORDS = {"let", "if", "else", "while", "print"}


def _skip_whitespace(
    source: str, index: int, line: int, column: int
) -> tuple[int, int, int]:
    """Advance past spaces, tabs, and newlines while keeping 1-based positions."""
    while index < len(source) and source[index] in " \t\r\n":
        if source[index] == "\n":
            line += 1
            column = 1
        elif source[index] == "\r":
            # Treat CRLF as one newline, and also support lone CR line endings.
            line += 1
            column = 1
            if index + 1 < len(source) and source[index + 1] == "\n":
                index += 1
        else:
            column += 1
        index += 1
    return index, line, column


class Lexer:
    def lex(self, source: str) -> tuple[list[Token], list[LexicalIssue]]:
        """Recognize the token types implemented so far."""
        tokens: list[Token] = []
        issues: list[LexicalIssue] = []
        index, line, column = 0, 1, 1
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        identifier_characters = letters + "0123456789_"
        single_character_tokens = {
            "+": TokenType.ARITH_OP,
            "-": TokenType.ARITH_OP,
            "*": TokenType.ARITH_OP,
            "/": TokenType.ARITH_OP,
            "%": TokenType.ARITH_OP,
            "=": TokenType.ASSIGN,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ";": TokenType.SEMICOLON,
        }

        while index < len(source):
            index, line, column = _skip_whitespace(source, index, line, column)
            if index >= len(source):
                break

            if source[index] == "#":
                while index < len(source) and source[index] not in "\r\n":
                    index += 1
                    column += 1
                continue

            if source[index] in "0123456789":
                start = index
                start_line, start_column = line, column
                while index < len(source) and source[index] in "0123456789":
                    index += 1
                    column += 1

                if index < len(source) and source[index] in identifier_characters:
                    while index < len(source) and source[index] in identifier_characters:
                        index += 1
                        column += 1
                    malformed = source[start:index]
                    issues.append(
                        LexicalIssue(
                            start_line,
                            start_column,
                            f"malformed token {malformed!r}",
                        )
                    )
                    continue

                tokens.append(
                    Token(
                        TokenType.INTEGER,
                        source[start:index],
                        start_line,
                        start_column,
                    )
                )
                continue

            if source[index] in letters:
                start = index
                start_line, start_column = line, column
                while (
                    index < len(source)
                    and source[index] in identifier_characters
                ):
                    index += 1
                    column += 1
                lexeme = source[start:index]
                token_type = (
                    TokenType.KEYWORD if lexeme in KEYWORDS else TokenType.IDENTIFIER
                )
                tokens.append(Token(token_type, lexeme, start_line, start_column))
                continue

            if source[index] in "!<>" or (
                source[index] == "="
                and index + 1 < len(source)
                and source[index + 1] == "="
            ):
                start = index
                start_line, start_column = line, column
                if index + 1 < len(source) and source[index + 1] == "=":
                    lexeme = source[index:index + 2]
                    index += 2
                    column += 2
                elif source[index] in "<>":
                    lexeme = source[index]
                    index += 1
                    column += 1
                else:
                    issues.append(
                        LexicalIssue(
                            start_line,
                            start_column,
                            f"invalid character {source[index]!r}",
                        )
                    )
                    index += 1
                    column += 1
                    continue
                tokens.append(Token(TokenType.REL_OP, lexeme, start_line, start_column))
                continue

            lexeme = source[index]
            if lexeme not in single_character_tokens:
                issues.append(
                    LexicalIssue(line, column, f"invalid character {lexeme!r}")
                )
                index += 1
                column += 1
                continue

            tokens.append(Token(single_character_tokens[lexeme], lexeme, line, column))
            index += 1
            column += 1

        return tokens, issues
