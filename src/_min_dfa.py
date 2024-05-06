from .models._automaton import Automaton
from .utils.structures.transition import Transition
from .utils.structures.state import State
import time


class MinimizedDeterministicFiniteAutomaton(Automaton):
    '''
    This class represents a minimized finite automaton.
    '''

    def __init__(self, dfa: Automaton, alphabet: set[str]) -> None:
        super().__init__()

        self.dfa: Automaton = dfa
        self.alphabet: set[str] = alphabet
        self.counter: int = 0

        self.build()

        self.nested = False
        self.leftMatch = None
        self.rightMatch = None

    def build(self):
        '''
        This method is made for build the automaton.

        Specific: Minimize the deterministic finite automaton.
        @Reference: Algorithm 3.39 : Minimizing the number of states of a DFA. Aho - Compilers: Principles, Techniques, and Tools (2nd Edition)
        '''
        F = [state.id for state in self.dfa.acceptanceStates]
        S_F = [state.id for state in self.dfa.states if state.id not in F]
        II = [F, S_F]

        IInew = self.partition(II)

        while IInew != II:
            II = IInew
            IInew = self.partition(II)

        IIfinal = II
        representatives = [group[0] for group in IIfinal]

        start_state = None
        for i, group in enumerate(IIfinal):
            if self.dfa.initialState.id in group:
                start_state = representatives[i]
                break

        acceptance_states = []
        for i, group in enumerate(IIfinal):
            if any(state.id in group for state in self.dfa.acceptanceStates):
                acceptance_states.append(representatives[i])

        transitions = []
        for i, group in enumerate(IIfinal):
            for a in self.alphabet:
                next_state = None
                for transition in self.dfa.transitions:
                    if transition.tail_id == representatives[i] and transition.using == a:
                        next_state = transition.head_id
                        break
                for j, next_group in enumerate(IIfinal):
                    if next_state in next_group:
                        transitions.append(Transition(
                            representatives[i], representatives[j], a))
                        break

        self.initialState = State(start_state, start_state, initial=True)
        self.states = [State(representative, representative)
                       for representative in representatives]
        self.acceptanceStates = [
            state for state in self.states if state.id in acceptance_states]
        self.transitions = transitions

    '''
    ↓↓ ALGORITHMS ↓↓
    '''

    def partition(self, II: list[list[int]]):
        IInew = []
        for G in II:
            subgroups = {}
            for id in G:
                key = []
                for a in self.alphabet:
                    next_state = None
                    for transition in self.dfa.transitions:
                        if transition.tail_id == id and transition.using == a:
                            next_state = transition.head_id
                            break
                    for i, group in enumerate(II):
                        if next_state in group:
                            if i != id:
                                key.append(i)
                                break
                key = tuple(key)
                if key not in subgroups:
                    subgroups[key] = []
                subgroups[key].append(id)

            IInew.extend(subgroups.values())

        return IInew
    '''
    ↑↑ END ALGORITHMS ↑↑
    '''

    def simulate(self, input: list):
        if not self.nested:
            return super().simulate(input)
        else:
            return self.nestedSimulation(input)

    def nestedSimulation(self, input: list):
        '''
        This method is made for simulate the automaton with nested mode.
        '''
        start_time = time.perf_counter()
        statePointer = self.initialState.id

        rightMatch = str(ord(self.rightMatch))
        leftMatch = str(ord(self.leftMatch))

        stack = []
        for idx, c in enumerate(input):
            if c == leftMatch:
                stack.append(c)
                for transition in self.transitions:
                    if transition.tail_id == statePointer and transition.using == c:
                        statePointer = transition.head_id
                        break
            elif c == rightMatch:
                if not stack or stack[-1] != leftMatch:
                    return False, idx
                stack.pop()
                if not stack:  # We've finished a complete match
                    for transition in self.transitions:
                        if transition.tail_id == statePointer and transition.using == c:
                            statePointer = transition.head_id
                            break
            else:
                found = False
                for transition in self.transitions:
                    if transition.tail_id == statePointer and transition.using == c:
                        statePointer = transition.head_id
                        found = True
                        break
                if not found:
                    return False, idx
        self.simulationTime = time.perf_counter() - start_time
        return (statePointer in [state.id for state in self.acceptanceStates] and not stack), len(input)
