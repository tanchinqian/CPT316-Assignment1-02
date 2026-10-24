"""Parser starter. Keep parser state explicit if using the recommended functional style."""
from .ast_nodes import ASTNode
from .tokens import Token


def parse_program(tokens: tuple[Token, ...], position: int = 0) -> tuple[ASTNode, int]:
    """TODO: recursive-descent parse from the transformed grammar; stop at first error.

    Return the AST and next token position without mutating input or global state.
    At program level, consume all tokens; len(tokens) represents end of input.
    Raise SyntaxIssue for the first syntax error. The CLI must not call this
    after any lexical issue has been reported.
    """
    raise NotImplementedError("Implement the KIRA parser")
