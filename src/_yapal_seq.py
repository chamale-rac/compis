from re import T


class YapalSequencer(object):
    """
    This class represents the YAPAL sequencer, which processes a list of tokens representing
    a grammar specification and extracts terminals, nonterminals, and productions.
    """

    def __init__(self, tokens) -> None:
        self.tokens = tokens

    def sequence(self):
        """
        This function processes the tokens and extracts terminals, nonterminals, and productions.
        """
        if self.splitBySpt():
            self.removeAnyCm()
            self.extractDefinitions()
            self.extractProductions()

            return True
        else:
            return False

    def splitBySpt(self):
        try:
            # Find the index of the split token
            split_index = self.tokens.index(('spt', '%%'))

            # Split the tokens into definitions and productions
            self.definitions = self.tokens[:split_index]
            self.productions = self.tokens[split_index+1:]

            return True
        except ValueError:
            # Split token not found
            return False

    def removeAnyCm(self):
        """
        This function removes any comments from the tokens.
        """
        self.tokens = [token for token in self.tokens if token[0] != 'cm']

    def extractDefinitions(self):
        """
        This function extracts the definitions from the tokens.
        """
        self.defined_tokens = set()
        self.ignore_tokens = set()

        flag_have_svd = False
        flag_have_ignore = False

        while self.definitions:
            # Extract the definition
            definition = self.definitions.pop(0)
            if definition[0] == 'nl':
                flag_have_svd = False
                flag_have_ignore = False
            elif definition[0] == 'svd':
                flag_have_svd = True
            elif flag_have_svd:
                if definition[0] == 'mayus':
                    self.defined_tokens.add(definition[1])
                    # TODO handle error minus here
            elif definition[0] == 'mayus' and definition[1] == 'IGNORE':
                flag_have_ignore = True
            elif flag_have_ignore:
                if definition[0] == 'mayus':
                    self.ignore_tokens.add(definition[1])

    def get_defined_tokens(self):
        """
        This function returns the defined tokens.
        """
        return self.defined_tokens

    def get_ignored_tokens(self):
        """
        This function returns the ignore tokens.
        """
        return self.ignore_tokens

    def extractProductions(self):
        """
        This function extracts the productions from the tokens.
        """
        self.terminals = []
        self.non_terminals = []
        self.defined_productions = []
        self.non_terminals_in_productions = []

        name = None
        has_name = False
        this_production = []
        this_productions = []

        while self.productions:
            # Extract the production
            production = self.productions.pop(0)

            if production[0] == 'minus' and has_name is not True:
                name = production[1]
            elif production[0] == 'stat':  # :
                has_name = True
            elif has_name and production[0] in ['mayus', 'minus']:
                this_production.append(production[1])
                if production[0] == 'mayus':
                    self.terminals.append(production[1])
                else:
                    self.non_terminals_in_productions.append(production[1])
            elif has_name and production[0] == 'rpt':  # |
                this_productions.append(this_production)
                this_production = []
            elif has_name and production[0] == 'end':  # ;
                this_productions.append(this_production)
                has_name = False
                self.non_terminals.append(name)
                this_production = []

                for production in this_productions:
                    self.defined_productions.append((name, tuple(production)))

                this_productions = []

        # Over terminal and non-terminal lists avoid repetitions but maintain order
        self.terminals = list(dict.fromkeys(self.terminals))
        self.non_terminals = list(dict.fromkeys(self.non_terminals))

        self.symbols = self.terminals + self.non_terminals

    def get_terminals(self):
        """
        This function returns the terminals.
        """
        return self.terminals

    def get_non_terminals(self):
        """
        This function returns the non-terminals.
        """
        return self.non_terminals

    def get_defined_productions(self):
        """
        This function returns the defined productions.
        """
        if len(self.defined_productions) == 0:
            return None
        return self.defined_productions

    def get_symbols(self):
        """
        This function returns the symbols.
        """
        return self.symbols

    def compare_tokens(self, tokens):
        """
        This function compares the tokens.
        """

        """
        Check that the defined tokens exist in the tokens
        If the token is in ignore_tokens, it is not necessary to check
        """
        mayus_tokens = []
        for token in tokens:
            # Convert token to uppercase
            mayus_tokens.append(token.upper())

        print(f"Yalex tokens: {mayus_tokens}")

        for token in self.defined_tokens:
            if token not in self.ignore_tokens:
                if token not in mayus_tokens:
                    return False

        return True

    def check_non_terminals_use(self):
        '''
        Check that all self.non_terminals_in_productions are in self.non_terminals
        '''
        for non_terminal in self.non_terminals_in_productions:
            if non_terminal not in self.non_terminals:
                return False

        return True
