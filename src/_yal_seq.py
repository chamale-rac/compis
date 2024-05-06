from src._tokenizer import Tokenizer
from src.utils.patterns import Pattern
from src.utils.constants import MATCH, EXIST, IDENT, VALUE, EXTRACT_REMINDER, SPECIAL, SPECIAL2
from src.utils.structures.symbol import Symbol
from src.utils.tools import errorsManager


class YalSequencer(object):
    '''
    This class represents the YAL sequencer.
    '''

    def __init__(self, lexer: Tokenizer, identSequence: list, exprContains: list[Pattern], extract: Pattern):
        '''
        This is the constructor of the class.
        Parameters: 
        - lexer: A lexer object.
        '''
        self.errorsManager = errorsManager()
        self.lexer: Tokenizer = lexer
        self.identSequence: list = identSequence
        self.functions: dict = {
            MATCH: self.match,
            EXIST: self.exist,
            IDENT: self.ident,
            VALUE: self.value,
            SPECIAL: self.special,
            SPECIAL2: self.special2,
            EXTRACT_REMINDER: None
        }
        self.idents: dict = {}
        self.exprContains: list[Pattern] = exprContains
        self.currentIdent: str = ""
        self.extract = extract
        self.reminders = []

    def extractIdent(self):
        '''
        This function returns the identifiers in the source code.
        '''
        symbolsPointer: int = 0
        sequencePointer: int = 0

        while symbolsPointer < len(self.lexer.symbolsTable):
            usingFunction: function = self.functions[self.identSequence[sequencePointer][1]]

            if usingFunction is None:
                if self.identSequence[sequencePointer][1] == EXTRACT_REMINDER:
                    # Reminders all the symbols that are after the last symbol that was processed.
                    self.reminders.extend(
                        self.lexer.symbolsTable[symbolsPointer:])
                    break

            functionResult = usingFunction(symbolsPointer, sequencePointer)

            if functionResult:
                sequencePointer += 1
                symbolsPointer += 1
                if sequencePointer >= len(self.identSequence):
                    sequencePointer = 0
            else:
                if sequencePointer > 0:
                    self.errorsManager.addError(
                        f'While verifying {self.identSequence[sequencePointer][0].name} is\did {self.identSequence[sequencePointer][1]} in sequence, over \"{self.lexer.symbolsTable[symbolsPointer].original}\" at position {self.lexer.symbolsTable[symbolsPointer].position}',
                        'Identity definition is not correct.'
                    )
                    break
                symbolsPointer += 1
                sequencePointer = 0

    def match(self, symbolsPointer: int, sequencePointer: int) -> bool:
        if not self.exist(symbolsPointer, sequencePointer):
            return False

        symbol: Symbol = self.lexer.symbolsTable[symbolsPointer]
        sequence: Pattern = self.identSequence[sequencePointer][0]

        lexer = Tokenizer()
        lexer.unCodified = symbol.original
        lexer.codified = symbol.content
        lexer.addPattern(sequence)
        lexer.tokenize(True)

        if len(lexer.symbolsTable) == 0:
            return False
        if len(lexer.symbolsTable) > 1:
            return False

        return True

    def ident(self, symbolsPointer: int, sequencePointer: int) -> bool:

        if not self.exist(symbolsPointer, sequencePointer):
            return False

        symbol: Symbol = self.lexer.symbolsTable[symbolsPointer]

        self.idents[symbol.original] = []
        self.currentIdent = symbol.original

        return True

    def value(self, symbolsPointer: int, sequencePointer: int) -> bool:

        if not self.exist(symbolsPointer, sequencePointer):
            return False

        symbol: Symbol = self.lexer.symbolsTable[symbolsPointer]
        value = []

        # TODO: Here I stop, at this point I need to implement the extraction and recognition of EXPR
        lexer = Tokenizer()
        lexer.unCodified = symbol.original
        lexer.codified = symbol.content
        lexer.addPatterns(self.exprContains)

        lexer.tokenize(False)

        if len(lexer.symbolsTable) > 0:
            for subSymbol in lexer.symbolsTable:
                if subSymbol.type == self.extract.name:
                    # Get the definition of the symbol, using the identifier. An looking on idents.
                    get_original = self.idents.get(subSymbol.original, None)

                    if get_original is None:
                        self.errorsManager.addError(
                            f'Previous definition of \"{subSymbol.original}\" not found',
                            f'Cant compose the value for the identity \"{self.currentIdent}\".'
                        )
                        return False

                    value.extend(
                        get_original
                    )
                else:
                    value.extend(subSymbol.original)

        self.idents[self.currentIdent] = value

        return True

    def exist(self, symbolsPointer: int, sequencePointer: int) -> bool:
        pattern: Pattern = self.identSequence[sequencePointer][0]
        symbol: Symbol = self.lexer.symbolsTable[symbolsPointer]

        if pattern.name != symbol.type:
            return False

        return True

    def special(self, symbolsPointer: int, sequencePointer: int) -> bool:
        symbol: Symbol = self.lexer.symbolsTable[symbolsPointer]
        if symbol.original == 'rule':
            return True
        return False

    def special2(self, symbolsPointer: int, sequencePointer: int) -> bool:
        symbol: Symbol = self.lexer.symbolsTable[symbolsPointer]
        if symbol.original == 'let':
            return True
        return False
