from src.utils.patterns import WS


class Symbol(object):
    '''
    This class represents a symbol.
    '''

    def __init__(self, type: str, content: str, original: str, position: int = None):
        '''
        This is the constructor of the class.
        Parameters:
        - name: The name of the symbol.
        - lexeme: The lexeme of the symbol.
        '''
        self.type: str = type
        self.content: str = content
        self.original: str = original
        self.position: int = position

    def __str__(self) -> str:
        '''
        This function returns the string representation of the symbol.
        '''
        if self.type == WS.name:
            return f'{self.type} -> '
        return f'{self.type} -> {self.original}'
