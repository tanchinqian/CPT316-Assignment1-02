# KIRA compiler front end

CPT316 Assignment 1, Semester 1 2026/2027, Group 02.
Python 3.10 or later; standard library only. No installation step is needed.

## Run

From this folder:

```powershell
python kira.py tests/public/public1_arithmetic_if.kira
```

The lexer, statement/block parser, expression/condition parser and text AST
formatter are implemented. Valid inputs print tokens, counts and the AST (status
0). Lexical errors skip parsing; syntax errors stop at the first error (status 1).

## Files and interfaces

| File | Purpose | Work remaining |
| --- | --- | --- |
| `kira.py` | File reading, phase order, basic output | Refine output and error handling as the components are implemented |
| `kira_frontend/tokens.py` | Frozen `Token(type, lexeme, line, column)` and token types | Use positions starting at 1 |
| `kira_frontend/lexer.py` | `Lexer().lex(source) -> (tokens, lexical_issues)` | Implemented; continue edge-case testing |
| `kira_frontend/parser.py` | Sharrvesh's functional statement/block parser; `parse_program(tokens, position=0) -> (tree, next_position)` | Integrated through the existing defaults |
| `kira_frontend/parser_support.py` | Shared `peek`, `expect`, error helpers and parser type aliases | Reuse from expression parsing |
| `kira_frontend/parser_expressions.py` | Member 3's `parse_expr` and `parse_cond` entry points | Implemented; ready for integration testing |
| `kira_frontend/ast_nodes.py` | Frozen `ASTNode(label, children)` and `format_ast(root)` | Text display implemented |
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

Member 3 has implemented these existing entry points:

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
The production expression parser and formatter are adapted from Sharrvesh's
supplied reference harness, with attribution retained. The original harness in
`tests/parser_harness.py` still supports the statement-parser tests.

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
2. Statements/blocks: implemented from Sharrvesh's deliverable; ready for
   integration testing with the production expression parser and formatter.
3. Expressions/AST: implemented with focused tests in `tests/test_expressions_ast.py`.
4. Member 4 handoff: validate the production components together, expand invalid
   input coverage, review crash/recursion-limit handling and prepare test evidence.
   Check phase skipping, syntax errors including EOF,
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
these checks validates the statement parser with that harness. The focused
expression/AST tests exercise production functions directly. Member 4 should
validate all six inputs through the standalone CLI and compare token counts,
AST structure and error locations with the official expected files.

## Member 4 error-handling validation

`tests/test_error_handling.py` exercises the production components without the
reference parser harness. It checks all six official CLI results, including each
token-type count (absent types mean zero), totals, exact valid ASTs and diagnostics.
Additional checks cover multiple lexical issues, resuming scanning, comments,
LF/CRLF/CR positions, phase skipping, first syntax error, empty/truncated input,
and the absence of semantic evaluation.

The CLI reports every lexical issue and explicitly says parsing was skipped.
Syntax failures report only the first `SyntaxIssue`; neither failure prints an
AST. File/encoding errors use argparse diagnostics on stderr. Exit statuses are
0 for success, 1 for lexical/syntax errors, and 2 for command-line/file failures
or an implementation recursion limit.

Parsing and AST formatting share a narrow `RecursionError` handler. Formatting
finishes before the AST heading is printed, so recursion failure cannot leave a
partial tree. The diagnostic identifies an implementation limit on stderr; it
does not mislabel a potentially valid program as a syntax error. This avoids an
uncaught traceback but does not remove the size/depth limitation of the recursive
parser and formatter. Do not claim that arbitrarily large inputs are supported.

Validation after this change: 35 unittest tests passed, including all six public
inputs through the production CLI. Run the command above to reproduce the checks.
The issue-format checks cover lexical, token-based syntax and EOF diagnostics.
Invalid-input checks also cover malformed numeric names, lone `!`, leading
underscores, decimals, missing delimiters, invalid conditions, unary minus,
empty blocks, block declarations, stray `else` and trailing tokens. `expect()`
uses the shared `raise_syntax_error()` helper for both mismatches and EOF.
`tests/public/README.txt` explains permitted output differences.
