"""
@File name: _expression.py
@Module: Regular Expression
@Author: Samuel Chamalé
@Date: 31/01/2024
@Description: This file contains main algorithms for the regular expression module.
"""

from src.utils.constants import RPAREN, LPAREN, OR, ZERO_OR_ONE, ONE_OR_MORE, KLEENE_STAR, CONCAT, OPERATORS_PRECEDENCE, TRIVIAL_CHARACTER_PRECEDENCE, LBRACKET, RBRACKET, SINGLE_QUOTE, DOUBLE_QUOTE, RANGE, WS, ANY_NOT_IN, UNIVERSE, HASHTAG
from src.utils.tools import errorsManager


class Expression(object):
    '''
    This class represents the regular expression module.
    '''

    def __init__(self, infixRegEx: str = None):
        '''
        This is the constructor of the class.
        Parameters:
        - infixRegEx: A regular expression in infix notation.
        '''
        self.errorsManager = errorsManager()
        self.infixRegEx: str = infixRegEx

    def hardProcess(self):
        '''
        This function processes the regular expression in infix notation.
        '''
        self.infixRegEx = self.hardCodify(self.infixRegEx)
        self.infixRegEx = self.transformGroupsOfCharacters(self.infixRegEx)
        self.infixRegEx = self.addExplicitConcatenation(self.infixRegEx)
        self.infixRegEx = self.shuntingYard(self.infixRegEx)
    '''
    ↓↓ ALGORITHMS ↓↓
    '''

    def shuntingYard(self, infixRegEx: str) -> str:
        '''
        Shunting Yard algorithm implementation, it takes a regular expression in infix notation and returns the regular expression in postfix notation.
        Parameters:
        - infixRegEx: A regular expression in infix notation. 
        Returns:
        - A regular expression in postfix notation.
        '''
        postfix = []
        stack = []

        for idx in range(len(infixRegEx)):
            c = infixRegEx[idx]
            if c == LPAREN:
                stack.append(c)
            elif c == RPAREN:
                while stack[-1] != LPAREN:
                    postfix += [stack.pop()]
                stack.pop()
            else:
                while stack:
                    peekedChar = stack[-1]
                    peekedCharPrecedence = self.getOperatorPrecedence(
                        peekedChar)
                    cPrecedence = self.getOperatorPrecedence(c)
                    if peekedCharPrecedence >= cPrecedence:
                        postfix += [stack.pop()]
                    else:
                        break
                stack.append(c)

        while stack:
            postfix += [stack.pop()]
        return postfix

    def addExplicitConcatenation(self, infixRegEx: list) -> str:
        '''
        This function takes a regular expression in infix notation and returns the regular expression with explicit concatenation operators.
        Parameters:
        - infixRegEx: A regular expression in infix notation.
        Returns:
        - A regular expression with explicit concatenation operators.
        '''
        res = []
        lenInfixRegEx = len(infixRegEx)
        for idx in range(lenInfixRegEx):
            c1 = infixRegEx[idx]
            if (idx + 1) < lenInfixRegEx:
                c2 = infixRegEx[idx + 1]
                res += [c1]
                if c1 not in [LPAREN, OR] and c2 != RPAREN and c2 not in [OR, ZERO_OR_ONE, ONE_OR_MORE, KLEENE_STAR]:
                    res += CONCAT
        res += [infixRegEx[-1]]
        return res

    '''
    ↑↑ END ALGORITHMS ↑↑
    '''

    '''
    ↓↓ ASSOCIATED FUNCTIONS ↓↓
    '''

    def getOperatorPrecedence(self, operator): return OPERATORS_PRECEDENCE.get(
        operator, TRIVIAL_CHARACTER_PRECEDENCE)

    def hardCodify(self, infixRegEx: str) -> list:
        '''
        This function takes a regular expression in infix notation and returns the regular expression codified using ascii codes.
        Parameters:
        - infixRegEx: A regular expression in infix notation.
        Returns:
        - A regular expression codified using ascii codes.
        '''
        result = []
        skip_next = False
        inside_single_quote = False
        inside_single_quote_len = 0
        inside_double_quote = False
        for c in infixRegEx:
            if skip_next:
                if c in ['n', 't', 's']:
                    translate = {
                        'n': '\n',
                        't': '\t',
                        's': ' '
                    }
                    result.append(str(ord(translate[c])))
                else:
                    result.append(str(ord(c)))
                skip_next = False
                if inside_single_quote:
                    inside_single_quote_len += 1
            elif c == '\\':
                skip_next = True
            elif c == DOUBLE_QUOTE:
                inside_double_quote = not inside_double_quote
            elif inside_double_quote:
                result.append(str(ord(c)))
            elif c == SINGLE_QUOTE:
                if inside_single_quote and inside_single_quote_len > 1:
                    raise ValueError(
                        "More than one character inside single quotes")
                inside_single_quote = not inside_single_quote
                inside_single_quote_len = 0
            elif inside_single_quote:
                result.append(str(ord(c)))
                inside_single_quote_len += 1
            elif c == '_':
                for i in range(256):
                    result.append(str(i))
                    if i != 255:
                        result.append(OR)
            elif c not in [LPAREN, RPAREN, OR, ZERO_OR_ONE, ONE_OR_MORE, KLEENE_STAR, CONCAT, LBRACKET, RBRACKET, DOUBLE_QUOTE, RANGE, WS, ANY_NOT_IN, HASHTAG]:
                result.append(str(ord(c)))
            else:
                result.append(c)
        return result

    def softCodify(self, infixRegEx: list) -> str:
        '''
        Characters to a list of ASCII codes.
        '''
        result = []
        for idx, c in enumerate(infixRegEx):
            if c == WS:
                # If is inside a quote add as ASCII code, else appends as is
                # Check have previous quote
                # If is not the first character
                if result[-1] in [str(ord(SINGLE_QUOTE))] and infixRegEx[idx+1] in [SINGLE_QUOTE]:
                    result.append(str(ord(c)))
                else:
                    result.append(c)
            else:
                result.append(str(ord(c)))
        return result

    def extraSoftCodify(self, infixRegEx: list) -> str:
        result = []
        for idx, c in enumerate(infixRegEx):
            result.append(str(ord(c)))
        return result

    def transformGroupsOfCharacters(self, infixRegEx: list) -> list:
        '''
        This function takes a regular expression in infix notation and returns the group of characters in the adequate format.
        Parameters:
        - infixRegEx: A regular expression in infix notation.
        Returns:
        - A list of characters.
        '''
        result = []
        idx = 0
        first_group = []

        while idx < len(infixRegEx):
            c = infixRegEx[idx]
            if c == LBRACKET:
                idx += 1
                group_result = []
                collected = []
                has_any_not_in = False
                extend_this = True

                if infixRegEx[idx] == ANY_NOT_IN:
                    has_any_not_in = True
                    idx += 1

                while infixRegEx[idx] != RBRACKET:
                    collected.append(infixRegEx[idx])
                    idx += 1

                for local_idx in range(len(collected)):
                    if collected[local_idx] == RANGE:

                        previous = collected[local_idx - 1]
                        next = collected[local_idx + 1]
                        for i in range(int(previous), int(next) + 1):
                            group_result.append(str(i))
                    else:
                        group_result.append(collected[local_idx])

                group_result = list(set(group_result))

                if has_any_not_in:
                    group_result = list(set(UNIVERSE) - set(group_result))

                if first_group != []:
                    group_result = list(
                        set(first_group) - set(group_result))
                    first_group = []

                idx += 1  # Skip the RBRACKET
                if idx < len(infixRegEx) and infixRegEx[idx] == HASHTAG:
                    first_group = group_result
                    extend_this = False
                    idx += 1

                if extend_this:
                    group_result.insert(0, LPAREN)
                    for i in range(2, len(group_result)*2, 2):
                        group_result.insert(i, OR)

                    group_result.pop()
                    group_result.append(RPAREN)

                    result.extend(
                        group_result
                    )
            else:
                result.append(c)
                idx += 1

        return result

    '''
    ↑↑ END ASSOCIATED FUNCTIONS ↑↑
    '''


"""
@References: https://gist.github.com/gbrolo/1a80f67f8d0a20d42828fb3fdb7be4de
"""
