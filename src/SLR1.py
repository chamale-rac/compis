from .LR0 import LR0
from tabulate import tabulate


class SLR1(object):
    def __init__(self, lr0) -> None:
        self.lr0: LR0 = lr0
        self.action = {}
        self.goto = {}

        self.construct_tables()

    def construct_tables(self):
        # Initialize ACTION and GOTO tables
        for state_idx, items in enumerate(self.lr0.C):
            self.action[state_idx] = {}
            self.goto[state_idx] = {}

            # Handle shift and goto entries
            for symbol in self.lr0.nonterminals.union(self.lr0.terminals):
                goto_result = self.lr0.goto(items, symbol)
                if goto_result:
                    goto_state = self.find_state(goto_result)
                    if symbol in self.lr0.nonterminals:
                        self.goto[state_idx][symbol] = goto_state
                    else:
                        self.action[state_idx][symbol] = ('shift', goto_state)

            for item in items:
                head, body, dot_position, is_kernel = item
                if dot_position == len(body):  # Check if the dot is at the end
                    if head == self.lr0.start_symbol:
                        self.action[state_idx]['$'] = ('accept',)
                    else:
                        prod_index = self.lr0.get_production_index(head, body)
                        for follow_symbol in self.lr0.follow_sets[head]:
                            self.action[state_idx][follow_symbol] = (
                                'reduce', prod_index)

    def LRparsing(self, input_list: list):
        stack = [0]  # start with initial state
        index = 0
        symbols = []
        input_symbols = input_list + ['$']  # append end marker
        log = []

        while True:
            current_state = stack[-1]
            current_symbol = input_symbols[index]
            action_entry = self.action.get(
                current_state, {}).get(current_symbol, None)

            # Log current step
            log.append({
                "Stack": stack[:],
                "Symbols": symbols[:],
                "Input": input_symbols[index:],
                "Action": action_entry if action_entry else "error"
            })

            if action_entry is None:
                # Handle error: Undefined action
                return log, "Error: No action defined for this state and symbol combination."

            action, *params = action_entry

            if action == 'shift':
                # Shift the next state onto the stack and move to the next symbol
                stack.append(params[0])
                symbols.append(current_symbol)
                index += 1

            elif action == 'reduce':
                # Reduce action: pop |β| symbols off the stack, find next state using GOTO, push onto stack
                production_index = params[0]
                head, body = self.lr0.productions[production_index]
                for _ in range(len(body)):
                    stack.pop()
                    symbols.pop()
                stack.append(self.goto[stack[-1]][head])
                symbols.append(head)

            elif action == 'accept':
                # Parsing successfully completed
                return log, "Accepted"

        # The while loop will always terminate with either a return on accept or error.

    def find_state(self, items):
        """
        Find the state index corresponding to the items
        """
        for idx, state_items in enumerate(self.lr0.C):
            if set(state_items) == set(items):  # Check if the items are the same
                return idx
        return None

    def table(self, terminals=None, nonterminals=None):
        # Get maximum row length for tabulate
        max_row_length = max(
            len(self.action), len(self.goto)) if self.action and self.goto else 0

        if not terminals:
            terminals = list(self.lr0.terminals)
        if not nonterminals:
            nonterminals = list(self.lr0.nonterminals)
            # From non_terminals remove the start symbol
            nonterminals.remove(self.lr0.start_symbol)

        terminals.append('$')

        rows = [idx for idx in range(max_row_length)]
        for idx in range(max_row_length):
            row = [idx]
            for symbol in terminals:
                if symbol in self.lr0.terminals or symbol == '$':
                    if idx in self.action and symbol in self.action[idx]:
                        row.append(self.action[idx][symbol])
                    elif idx in self.goto and symbol in self.goto[idx]:
                        row.append(self.goto[idx][symbol])
                    else:
                        row.append('')
            for symbol in nonterminals:
                if idx in self.goto and symbol in self.goto[idx]:
                    row.append(self.goto[idx][symbol])
                else:
                    row.append('')
            rows[idx] = row

        headers = ['State'] + terminals + nonterminals  # Header for the table

        slr_table = tabulate(rows, headers=headers, tablefmt='grid')

        return slr_table
