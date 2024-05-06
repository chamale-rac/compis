from graphviz import Digraph


class Grammar(object):
    def __init__(self, productions) -> None:
        self.productions = productions
        self.start_symbol = productions[0][0]
        self.nonterminals = {prod[0] for prod in productions}
        self.relations = []

    def augment(self) -> None:
        new_start_symbol = f"{self.start_symbol}'"
        new_start_production = (new_start_symbol, (self.start_symbol,))
        self.productions.insert(0, new_start_production)
        self.nonterminals.add(new_start_symbol)
        self.start_symbol = new_start_symbol

    def closure(self, items) -> None:
        items = [
            (item[0], item[1], item[2]) for item in items
        ]

        closure_set = set(items)
        kernel_items = set()

        for item in items:
            kernel_items.add(item)

        while True:
            new_items = set()
            for (head, body, dot_position) in closure_set:
                # Only proceed if the dot is before a non-terminal and not at the end of the production
                if dot_position < len(body) and body[dot_position] in self.nonterminals:
                    B = body[dot_position]
                    for production in self.productions:
                        if production[0] == B:
                            # For each production B -> γ, add B -> .γ to the closure if not already present
                            new_item = (B, production[1], 0)
                            if new_item not in closure_set:
                                # And is not empty
                                new_items.add(new_item)

                    if dot_position > 0:
                        kernel_items.add((head, body, dot_position))

            if not new_items:
                break

            closure_set.update(new_items)

        non_kernel_items = closure_set - kernel_items

        closure_set = set()

        # To all the non_kernel_items add the 4th parameter as False
        for item in non_kernel_items:
            head, body, dot_position = item
            if body != ():  # Removing the empty ones
                closure_set.add((head, body, dot_position, False))

        # To all the kernel_items add the 4th parameter as True
        for item in kernel_items:
            head, body, dot_position = item
            closure_set.add((head, body, dot_position, True))

        return closure_set

    def goto(self, items, symbol) -> None:
        goto_items = set()

        for item in items:
            head, body, dot_position, is_kernel = item
            if dot_position < len(body) and body[dot_position] == symbol:
                new_item = (head, body, dot_position + 1, True)
                goto_items |= self.closure({new_item})

        return goto_items

    def items(self, symbols):
        relations = []

        C = [self.closure(
            {(self.start_symbol, self.productions[0][1], 0, True)})]

        # A dictionary to map sets in C to their indices
        set_indices = {frozenset(C[0]): 0}

        while True:
            new_sets_added = False
            for I_index, I in enumerate(C):
                for X in symbols:
                    goto_set = self.goto(I, X)
                    goto_frozenset = frozenset(goto_set)

                    if goto_set:
                        if goto_frozenset not in set_indices:
                            C.append(goto_set)
                            set_indices[goto_frozenset] = len(C) - 1
                            new_sets_added = True
                        # Regardless of whether it's new or existing, record the transition
                        relations.append(
                            (I_index, set_indices[goto_frozenset], X))

                        for item in goto_set:
                            # Check have start symbol in the head and dot is at the end of the production
                            if item[0] == self.start_symbol and item[2] == len(item[1]):
                                relations.append(
                                    (set_indices[goto_frozenset], 'accept', ''))
                                continue
            if not new_sets_added:
                break

        # Avoid duplicates in relations
        relations = list(set(relations))

        return C, relations

    def items_to_str_print(self, items):
        def item_to_str(item):
            before_dot = ' '.join(item[1][:item[2]])
            after_dot = ' '.join(item[1][item[2]:])
            return f"\t\t{item[0]} → {before_dot} • {after_dot}"

        kernel_items_str = '\n'.join(item_to_str(item)
                                     for item in items if item[3])
        non_kernel_items_str = '\n'.join(
            item_to_str(item) for item in items if not item[3])

        return f"\t  Kernel items: \n{kernel_items_str}\n\t  Non-kernel items: \n{non_kernel_items_str}"

    def items_to_str(self, items):
        def item_to_str(item):
            before_dot = ' '.join(item[1][:item[2]])
            after_dot = ' '.join(item[1][item[2]:])
            return f"{item[0]} → {before_dot} • {after_dot}"

        kernel_items_str = '\\l'.join(item_to_str(item)
                                      for item in items if item[3])
        non_kernel_items_str = '\\l'.join(
            item_to_str(item) for item in items if not item[3])

        combined_str = f"{kernel_items_str} | {non_kernel_items_str}" if non_kernel_items_str else kernel_items_str
        return f'{combined_str}'

    def draw(self, C, relations, label: str = None):
        G = Digraph(
            graph_attr={'rankdir': 'TB'},
            node_attr={'shape': 'record'}
        )

        G.attr(label=label)

        for idx, I in enumerate(C):
            node_label = self.items_to_str(I)
            G.node(f"I{idx}", label=f"{{ I{idx} | {node_label} }}")

        for idx, relation in enumerate(relations):
            i, j, X = relation
            G.edge(f"I{i}", f"I{j}", label=" " + X + " ")

        try:
            G.render('LRautomaton', format='png', cleanup=True)
        except Exception as e:
            print(e)

    def __str__(self) -> str:
        """
        Converting each production to -> separated string and joining them with newline
        """
        return '\n'.join(f"\t[{idx}] {head} -> {' '.join(body)}" for idx, (head, body) in enumerate(self.productions))

    def compute_first(self):

        self.first_sets = {symbol: set() for symbol in self.nonterminals}
        # Initialize FIRST for terminals in each production
        for head, production in self.productions:
            for symbol in production:
                if symbol not in self.nonterminals:  # Terminal found directly in production
                    self.first_sets[head].add(symbol)
                    break  # Stop at the first terminal since it determines the FIRST set directly

        # Iteratively propagate FIRST sets based on non-terminals
        changed = True
        while changed:
            changed = False
            for head, production in self.productions:
                first_len_before = len(self.first_sets[head])
                i = 0
                while i < len(production):
                    symbol = production[i]
                    if symbol in self.nonterminals:
                        # Add non-ε symbols from FIRST(symbol) to FIRST(head)
                        non_epsilon = self.first_sets[symbol] - {'ε'}
                        self.first_sets[head].update(non_epsilon)
                        if 'ε' not in self.first_sets[symbol]:
                            break
                    else:
                        # First terminal encountered determines the FIRST set
                        self.first_sets[head].add(symbol)
                        break
                    i += 1
                else:
                    # If all symbols can derive ε, add ε to FIRST(head)
                    self.first_sets[head].add('ε')

                # Check if set changed in size
                if first_len_before != len(self.first_sets[head]):
                    changed = True

    def compute_follow(self):
        pass
