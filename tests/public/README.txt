CPT316 Assignment 1, Semester 1 2026/2027
KIRA public test programs
=========================================

This pack has six KIRA test programs. Each one comes with a file showing
the expected result:

    publicN_name.kira            the test program
    publicN_name.expected.txt    what a correct lexer and parser report

Run your program on each .kira file and compare your output with the
.expected.txt file.

What must match
---------------
  - Token counts: the total and the count for each token type.
  - AST: the same node names, in the same order, with the same nesting.
    Use the node names and the two-space indentation given in the brief.
  - Errors: the same error type and the same line number.

What may be different
---------------------
  - The layout of your token stream and your headings.
  - The wording of your error messages.
  - Column numbers. Report a column for every error, but it is not
    compared in marking.

The six tests
-------------
  File                               Tests                        Expected result
  public1_arithmetic_if.kira         precedence, ( ), if/else     91 tokens, AST
  public2_while.kira                 while loops, nested if       80 tokens, AST
  public3_nested_blocks.kira         nested blocks, no spaces     100 tokens, AST
                                     between tokens
  public4_lexical_errors.kira        two lexical errors           LexicalError at line 4
                                                                  and at line 5; no AST
  public5_syntax_error.kira          missing ')'                  SyntaxError at line 3
  public6_syntax_end_of_input.kira   missing '}'                  SyntaxError at end of
                                                                  input

Reminders
---------
  - If the lexer reports an error, the parser does not run.
  - Lexical errors: report every one in the file.
    Syntax errors: stop at the first one.
  - Your program does not check whether variables are declared and does
    not run the KIRA program. A program that uses an undeclared variable
    is still valid for the lexer and parser.
  - Passing these six tests does not guarantee full marks. Marking also
    uses hidden test programs of the same kind, so try your program on
    other inputs as well.
