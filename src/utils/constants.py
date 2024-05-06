"""
@File name: constants.py
@Module: Utils
@Author: Samuel Chamalé
@Date: 31/01/2024
@Description: Contains the constants used in the implementation of the compiler.
"""

EPSILON = 'ϵ'
LPAREN = '('
RPAREN = ')'
LBRACKET = '['
RBRACKET = ']'
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
RANGE = '-'
OR = '|'
CONCAT = '•'
ZERO_OR_ONE = '?'
ONE_OR_MORE = '+'
KLEENE_STAR = '*'
TERMINATOR = 'TERMINATOR'
HASHTAG = '#'
WS = ' '
ANY_NOT_IN = '^'

OPERATORS_PRECEDENCE = {LPAREN: 1, OR: 2, CONCAT: 3, ZERO_OR_ONE: 4,
                        ONE_OR_MORE: 4, KLEENE_STAR: 4}

TRIVIAL_CHARACTER_PRECEDENCE = 6

IDENT = 'IDENT'
VALUE = 'VALUE'
MATCH = 'MATCH'
EXIST = 'EXIST'
SPECIAL = 'SPECIAL'
SPECIAL2 = 'SPECIAL2'
EXTRACT_REMINDER = 'EXTRACT_REMINDER'

UNIVERSE = set(str(i) for i in range(256))
