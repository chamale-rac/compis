from src.utils.structures.state import State
from src.utils.structures.transition import Transition
from graphviz import Digraph
import time


class Automaton(object):
    '''
    This class represents a finite automaton. Can be used for NFA and DFA, it depends on the implementation.
    '''

    def __init__(self) -> None:
        self.states: list[State] = []
        self.initialState: State = None
        self.acceptanceStates: list[State] = []
        self.transitions: list[Transition] = []
        self.simulationTime: float = 0

    def preprocess(self):
        '''
        This method is made for preprocess the automaton.
        '''
        raise NotImplementedError()

    def process(self):
        '''
        This method is made for process the automaton.
        '''
        raise NotImplementedError()

    def build(self):
        '''
        This method is made for build the automaton.
        '''
        raise NotImplementedError()

    def postprocessing(self):
        '''
        This method is made for postprocessing the automaton.
        '''
        raise NotImplementedError()

    def draw(self, name: str, id: int, label: str = None):
        '''
        This method is made for draw the automaton.
        '''
        dot = Digraph(
            graph_attr={
                'rankdir': 'LR',
            }
        )

        # Set the label
        dot.attr(label=label)

        # Draw the special start indicator
        dot.node('start', 'start', shape='point', color='transparent')

        # Draw the transitions
        for transition in self.transitions:
            dot.edge(str(transition.tail_id), str(
                transition.head_id), str(transition.using))

        # Draw the states
        for state in self.states:
            dot.node(str(state.id), str(state.value))

        # Create connection between start and initial state
        dot.edge('start', str(self.initialState.id), 'start')

        # Reshape the acceptance states
        for state in self.acceptanceStates:
            dot.node(str(state.id), str(state.value), shape='doublecircle')

        dot.render(f'{id}/{name}', format='png', cleanup=True)

    def simulate(self, input: list):
        '''
        This method is made for simulate the automaton.
        '''
        start_time = time.perf_counter()
        statePointer = self.initialState.id
        for idx, c in enumerate(input):
            found = False
            for transition in self.transitions:
                if transition.tail_id == statePointer and transition.using == c:
                    statePointer = transition.head_id
                    found = True
                    break
            if not found:
                return False, idx
        self.simulationTime = time.perf_counter() - start_time
        return statePointer in [state.id for state in self.acceptanceStates], len(input)
