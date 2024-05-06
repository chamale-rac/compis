from src.utils.patterns import Pattern
from src.utils.structures.symbol import Symbol
from src._expression import Expression
from src.utils.tools import errorsManager


class Tokenizer(object):
    '''
    This class represents the lexer module.
    '''

    def __init__(self, sourceCode: str = None, useExtraSoftCodify: bool = False):
        '''
        This is the constructor of the class.
        Parameters:
        - sourceCode: The source code to be tokenized.
        '''
        self.useExtraSoftCodify = useExtraSoftCodify
        self.sourceCode: str = sourceCode
        if sourceCode is not None:
            self.codifySourceCode()
        self.patterns: dict = {}
        self.sequences: dict = {}
        self.symbolsTable: list[Symbol] = []
        self.errorsManager = errorsManager()

    def addPatterns(self, patterns: list[Pattern]) -> None:
        '''
        This function adds a list of patterns to the patterns dictionary.
        Parameters:
        - patterns: A list of pattern objects.
        '''
        for pattern in patterns:
            self.addPattern(pattern)

    def addPattern(self, pattern: Pattern) -> None:
        '''
        This function adds a pattern to the patterns dictionary.
        Parameters:
        - pattern: A pattern object.
        '''
        self.patterns[pattern.name] = pattern

    def codifySourceCode(self):
        '''
        This function codifies the source code.
        '''
        self.expr = Expression(self.sourceCode)

        self.unCodified = self.expr.infixRegEx
        if not self.useExtraSoftCodify:
            self.codified = self.expr.softCodify(
                self.expr.infixRegEx
            )
        else:
            self.codified = self.expr.extraSoftCodify(
                self.expr.infixRegEx
            )

    def removeSymbols(self, withPatterns: list[Pattern]):
        '''
        This function removes the symbols that are in the withPatterns list.
        Parameters:
        - withPatterns: A list of patterns.
        '''
        self.symbolsTable: list[Symbol] = list(
            filter(lambda symbol: symbol.type not in [pattern.name for pattern in withPatterns],
                   self.symbolsTable)
        )

    def removeAndCollectSymbols(self, withPatterns: list[Pattern]):
        '''
        This function removes the symbols that are in the withPatterns list and returns them.
        Parameters:
        - withPatterns: A list of patterns.
        '''
        removedSymbols = list(
            filter(lambda symbol: symbol.type in [pattern.name for pattern in withPatterns],
                   self.symbolsTable)
        )
        self.symbolsTable: list[Symbol] = list(
            filter(lambda symbol: symbol.type not in [pattern.name for pattern in withPatterns],
                   self.symbolsTable)
        )
        return removedSymbols

    def removeSymbolsByMatch(self, withPattern: Pattern):
        removedAmount = 0
        internal_lexer = Tokenizer()
        internal_lexer.addPatterns([withPattern])
        for symbol in self.symbolsTable:
            if symbol.type != withPattern.name:
                continue

            internal_lexer.codified = symbol.content
            internal_lexer.unCodified = symbol.original
            internal_lexer.tokenize()

            if len(internal_lexer.symbolsTable) != 0:
                self.symbolsTable.remove(symbol)
                removedAmount += 1

        return removedAmount

    def addSequence(self, sequenceID: str, sequence: list):
        '''
        This function adds a sequence to the sequences dictionary.
        Parameters:
        - sequenceID: The id of the sequence.
        - sequence: The sequence to be added.
        '''
        self.sequences[sequenceID] = sequence

    def tokenize(self, usingLongestMatch: bool = True):
        '''
        This function tokenizes the source code.
        '''
        # This pointer will point to the current character being analyzed.

        forward = 0
        # Strategy:
        # 1. Iterate over the source code.
        # 2. For each character in the source code, check if the current character is a prefix of any pattern.
        # This will be done by sending the entire source code to the DFAs of each pattern.
        # If it is true, then we will get the longest match, and update the lexemeBegin and forward pointers.

        codified = self.codified
        unCodified = self.unCodified

        while forward < len(codified):
            match = None
            for pattern in self.patterns.values():
                _, idx = pattern.min_dir_dfa.simulate(
                    codified[forward:]
                )
                if match is None:
                    if idx > 0:
                        match = (pattern.name, idx)
                else:
                    if usingLongestMatch:
                        if idx > match[1]:
                            match = (pattern.name, idx)
                    else:
                        if idx < match[1] and idx > 0:
                            match = (pattern.name, idx)
            if match is not None:
                # Save also the original
                self.symbolsTable.append(Symbol(
                    match[0], codified[forward:forward + match[1]], unCodified[forward:forward + match[1]], forward))
                forward += match[1]
            else:
                self.errorsManager.addError(
                    f'No pattern found for character \"{unCodified[forward]}\" at position \"{forward}\"', 'Not all characters were tokenized')
                break
