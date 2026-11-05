# KIRA compiler front end

CPT316 Assignment 1, Semester 1 2026/2027, Group 02.
Python 3.10 or later; standard library only. No installation step is needed.

## Run

From this folder:

```powershell
python kira.py tests/public/public1_arithmetic_if.kira
```

The lexer and Member 2 statement/block parser are implemented. Member 3's
production expression parser, condition parser and AST display are still pending.
For this valid input the command prints tokens and counts, then reports
`Starter TODO: Implement Member 3 expression parsing` and exits with status 2.
Inputs with lexical errors report those errors and skip parsing (status 1).

## Files and interfaces

| File | Purpose | Work remaining |
| --- | --- | --- |
| `kira.py` | File reading, phase order, basic output | Refine output and error handling as the components are implemented |
| `kira_frontend/tokens.py` | Frozen `Token(type, lexeme, line, column)` and token types | Use positions starting at 1 |
| `kira_frontend/lexer.py` | `Lexer().lex(source) -> (tokens, lexical_issues)` | Implemented; continue edge-case testing |
| `kira_frontend/parser.py` | Sharrvesh's functional statement/block parser; `parse_program(tokens, position=0) -> (tree, next_position)` | Connect Member 3's implementations through the existing defaults |
| `kira_frontend/parser_support.py` | Shared `peek`, `expect`, error helpers and parser type aliases | Reuse from expression parsing |
| `kira_frontend/parser_expressions.py` | Member 3's `parse_expr` and `parse_cond` entry points | Implement arithmetic expressions and relational conditions |
| `kira_frontend/ast_nodes.py` | Frozen `ASTNode(label, children)` and `format_ast(root)` stub | Build the required tree and implement text display |
| `kira_frontend/errors.py` | Lexical issue record and syntax exception | Create issues at the correct source locations |
| `tests/public/` | Six official inputs, expected results, and original test-pack README | Run and compare after implementation |
| `tests/test_starter.py` | Smoke checks for the scaffold | Add compiler tests as the team implements it |
| `tests/test_parser.py` | Statement/block and CLI integration tests | Currently injects the reference expression/display harness |
| `tests/parser_harness.py` | Sharrvesh's standalone expression/display reference from his document | Test support only; not imported by production code |

The parser receives an immutable tuple of tokens with no extra EOF token.
The position after the last token is `len(tokens)`. Parsing functions should
pass positions explicitly and return the next position, without modifying the
token stream or using global state. The program parser must consume all tokens.
AST children are tuples. Raise `SyntaxIssue` for the first syntax error; use
`at_end_of_input=True` when no token remains.

## Member 2 contribution and Member 3 handoff

The statement/block parsing logic and standalone test harness were supplied by
Sharrvesh in `CPT316- Sharrvesh.docx`. This repository port preserves his grammar
and recursive parsing structure. Integration changes reuse the shared data
classes, use `Token.column`, raise `SyntaxIssue` with explicit EOF handling, and
adapt `parse_program` to accept a starting position and return the next position.
The port and regression tests are integration work; the original Member 2 parser
contribution belongs to Sharrvesh.

Member 3 should implement these existing entry points:

```python
parse_expr(tokens: tuple[Token, ...], position: int) -> tuple[ASTNode, int]
parse_cond(tokens: tuple[Token, ...], position: int) -> tuple[ASTNode, int]
format_ast(root: ASTNode) -> str
```

The first two belong in `parser_expressions.py`; the formatter belongs in
`ast_nodes.py`. Expression functions return the position immediately after the
expression, leaving statement delimiters for Member 2's parser. Conditions
consume `expr REL_OP expr`. Use `BinOp <op>`, `RelOp <op>`, `Id <name>` and
`Int <value>` labels; preserve precedence and left associativity. Parentheses
affect the tree shape but do not create nodes. Display one node per line with
two spaces per level. Import shared helpers from `parser_support.py` to avoid
circular imports with the statement parser.

`parse_program` also accepts keyword-only `parse_expr` and `parse_cond` callbacks
for independent testing. Without overrides it calls the production entry points.
The reference functions in `tests/parser_harness.py` are explicitly test support,
not a completed Member 3 submission.

Member 2's transformed structural grammar is:

```text
program        -> item_list
item_list      -> item item_list_tail
item_list_tail -> item item_list_tail | epsilon
item           -> decl | stmt
decl           -> 'let' id '=' expr ';'
stmt           -> assign | if_stmt | while_stmt | print_stmt
assign         -> id '=' expr ';'
if_stmt        -> 'if' '(' cond ')' block else_part
else_part      -> 'else' block | epsilon
while_stmt     -> 'while' '(' cond ')' block
print_stmt     -> 'print' '(' expr ')' ';'
block          -> '{' stmt_list '}'
stmt_list      -> stmt stmt_list_tail
stmt_list_tail -> stmt stmt_list_tail | epsilon
```

The list rules remove left recursion; `else_part` factors the common `if`
prefix. These list functions use right recursion, not tail recursion: tuple
concatenation occurs after the recursive call returns. Very long sequences or
deeply nested blocks can exceed Python's recursion limit; this remains a
limitation to address before claiming unrestricted input support.

## Remaining team work

1. Lexer: extend edge-case coverage beyond the public fixtures.
2. Statements/blocks: implemented from Sharrvesh's deliverable; check integration
   again when Member 3's production functions are ready.
3. Expressions/AST: implement precedence and left associativity, conditions,
   required AST node labels/child order, and two-space-indented display.
4. Error handling/testing: check phase skipping, syntax errors including EOF,
   output counts, and all six official test pairs.

Declarations belong only at the top level. There is no unary minus, semantic
analysis, or program execution. The current brief and official expected results
are the references for the finished implementation.

## Run the checks

```powershell
python -m unittest discover -s tests -v
```

The tests compare all three valid public ASTs and both public syntax errors,
exercise lexical-error phase skipping, and reject invalid statement/block forms.
CLI integration tests inject Sharrvesh's expression/display harness. Passing
these checks validates the Member 2 port with that harness; it does not mean
Member 3's production functions are implemented or the standalone CLI is complete.
After Member 3's implementation, run all six inputs through the standalone CLI
and compare token counts, AST structure and error locations with the official
expected files. `tests/public/README.txt` explains permitted output differences.
