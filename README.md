# KIRA compiler front end - starter template

CPT316 Assignment 1, Semester 1 2026/2027, Group 02.
Python 3.10 or later; standard library only. No installation step is needed.

## Run

From this folder:

```powershell
python kira.py tests/public/public1_arithmetic_if.kira
```

This is an incomplete scaffold. The command currently prints
`Starter TODO: Implement the KIRA lexer` and exits with status 2.
It does not yet tokenize, parse, or pass the public compiler tests.

## Files and interfaces

| File | Purpose | Work remaining |
| --- | --- | --- |
| `kira.py` | File reading, phase order, basic output | Refine output and error handling as the components are implemented |
| `kira_frontend/tokens.py` | Frozen `Token(type, lexeme, line, column)` and token types | Use positions starting at 1 |
| `kira_frontend/lexer.py` | `Lexer().lex(source) -> (tokens, lexical_issues)` | Implement scanning in imperative/object-oriented style |
| `kira_frontend/parser.py` | `parse_program(tokens, position) -> (tree, next_position)` | Transform the grammar, then implement functional recursive descent |
| `kira_frontend/ast_nodes.py` | Frozen `ASTNode(label, children)` and `format_ast(root)` stub | Build the required tree and implement text display |
| `kira_frontend/errors.py` | Lexical issue record and syntax exception | Create issues at the correct source locations |
| `tests/public/` | Six official inputs, expected results, and original test-pack README | Run and compare after implementation |
| `tests/test_starter.py` | Smoke checks for the scaffold | Add compiler tests as the team implements it |

The parser receives an immutable tuple of tokens with no extra EOF token.
The position after the last token is `len(tokens)`. Parsing functions should
pass positions explicitly and return the next position, without modifying the
token stream or using global state. The program parser must consume all tokens.
AST children are tuples. Raise `SyntaxIssue` for the first syntax error; use
`at_end_of_input=True` when no token remains.

## Team starting points

1. Lexer: implement token recognition, whitespace/comments, positions, and collect
   every lexical issue. Return recognized tokens and issues in source order.
2. Statements/blocks: agree on the transformed grammar and implement top-level
   declarations, assignments, if/else, while, print, and nonempty blocks.
3. Expressions/AST: implement precedence and left associativity, conditions,
   required AST node labels/child order, and two-space-indented display.
4. Error handling/testing: check phase skipping, syntax errors including EOF,
   output counts, and all six official test pairs.

Declarations belong only at the top level. There is no unary minus, semantic
analysis, or program execution. The current brief and official expected results
are the references for the finished implementation.

## Check the scaffold

```powershell
python -m unittest discover -s tests -v
```

These checks verify startup and scaffold contracts; they do not validate a
compiler. After implementation, run each `tests/public/*.kira` input and compare
token counts, AST structure, and error types/lines with its `.expected.txt` file.
The official `tests/public/README.txt` explains permitted output differences.
