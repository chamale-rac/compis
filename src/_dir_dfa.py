from .models._automaton import Automaton
from .utils.structures.tree_node import TreeNode
from .utils.structures.state import State
from .utils.structures.transition import Transition
from .utils.constants import EPSILON, OR, CONCAT, KLEENE_STAR, TERMINATOR
from collections import defaultdict

from .utils.tools import numberToLetter
import time


class DirectDeterministicFiniteAutomaton(Automaton):
    '''
    This class represents a direct deterministic finite automaton.
    '''

    def __init__(self, abstractSyntaxTree: TreeNode) -> None:
        '''
        This is the constructor of the class.
        Parameters:
        - ast: The abstract syntax tree of a regular expression.
        '''
        super().__init__()

        self.abstractSyntaxTree: TreeNode = abstractSyntaxTree
        self.symbols: dict = dict()
        self.followPosDict: dict = dict()
        self.counter: int = 0

        self.returnDict = {}

        self.preprocess()
        self.process()
        self.build()
        self.postprocessing()

    def preprocess(self):
        '''
        This method is made for preprocess the automaton.

        Specific: Transform the Abstract Syntax Tree nodes to a custom class that has all the information we need.
        '''
        newRoot = TreeNode(CONCAT, TreeNode(TERMINATOR),
                           self.abstractSyntaxTree)
        self.abstractSyntaxTree = newRoot
        self.abstractSyntaxTree.postOrderTraversal(self.toCustomNode)

    def process(self):
        '''
        This method is made for process the automaton.

        Specific: Get the nullable, firstPos, lastPos and followPos of the nodes of the Abstract Syntax Tree.
        '''
        self.abstractSyntaxTree.postOrderTraversal(self.nullable)
        self.abstractSyntaxTree.postOrderTraversal(self.firstAndLastPos)
        self.abstractSyntaxTree.postOrderTraversal(self.followPos)

    def build(self):
        '''
        This method is made for build the automaton.

        Specific: Build the direct deterministic finite automaton.
        @Reference: Figure 3.62: Construction of a DFA directly from a regular expression. Aho - Compilers: Principles, Techniques, and Tools (2nd Edition)
        '''
        initialState = State(
            self.abstractSyntaxTree.value.firstPos, id=0, initial=True)
        self.initialState = initialState
        self.states.append(initialState)
        self.counter = 1

        while any(not state.marked for state in self.states):
            S = next(state for state in self.states if not state.marked)
            S.marked = True

            symbols = defaultdict(list)
            for id in S.value:
                symbol = self.symbols[id]
                symbols[symbol].append(id)

            for symbol in symbols:
                if symbol != TERMINATOR:
                    U = set()
                    for id in symbols[symbol]:
                        U = U.union(self.followPosDict.get(id, set()))
                    if not any(state.value == U for state in self.states):
                        self.states.append(State(U, self.counter))
                        self.counter += 1
                    U = next(state for state in self.states if state.value == U)
                    self.transitions.append(Transition(S.id, U.id, symbol))
                else:
                    S.acceptance = True
                    self.acceptanceStates.append(S)

    def postprocessing(self):
        '''
        This method is made for postprocessing the automaton. And rename the state.value to letters based on the state.id
        '''
        for state in self.states:
            state.value = state.id

    '''
    ↓↓ INNER CLASSES ↓↓
    '''
    class CustomNode(object):
        '''
        This class represents a custom node for the direct deterministic finite automaton.
        '''

        def __init__(self, value: str, id: int, firstPos: set = set(), lastPos: set = set(), nullable: bool = None) -> None:
            '''
            This is the constructor of the class.
            Parameters:
            - value: The value of the node.
            - firstPos: The first position set of the node.
            - lastPos: The last position set of the node.
            - nullable: The nullable property of the node.
            '''
            self.value: str = value
            self.id: int = id
            self.firstPos: set = firstPos
            self.lastPos: set = lastPos
            self.nullable: bool = nullable
    '''
    ↑↑ END INNER CLASSES ↑↑
    '''

    '''
    ↓↓ ASSOCIATED FUNCTIONS ↓↓
    '''

    def toCustomNode(self,  node: TreeNode):
        '''
        This function is made for transform a TreeNode to a CustomNode.
        '''

        if node.value not in [EPSILON, OR, CONCAT, KLEENE_STAR]:
            self.counter += 1
            self.symbols[self.counter] = node.value
            node.value = self.CustomNode(node.value, self.counter)
        else:
            node.value = self.CustomNode(node.value, None)
    '''
    ↑↑ END ASSOCIATED FUNCTIONS ↑↑
    '''

    '''
    ↓↓ ALGORITHMS ↓↓
    '''

    def nullable(self, node: TreeNode):
        '''
        This function modifies the nullable attribute of the node.
        '''
        if node.value.value == EPSILON:
            node.value.nullable = True
        elif node.value.value == OR:
            node.value.nullable = node.left.value.nullable or node.right.value.nullable
        elif node.value.value == CONCAT:
            node.value.nullable = node.left.value.nullable and node.right.value.nullable
        elif node.value.value == KLEENE_STAR:
            node.value.nullable = True
        else:
            node.value.nullable = False

    def firstAndLastPos(self, node: TreeNode) -> set:
        '''
        This function modifies the firstPos and lastPos attributes of the node.
        '''
        if node.value.value == EPSILON:
            node.value.firstPos = set()
            node.value.lastPos = set()
        elif node.value.value == OR:
            node.value.firstPos = node.left.value.firstPos.union(
                node.right.value.firstPos)
            node.value.lastPos = node.left.value.lastPos.union(
                node.right.value.lastPos)
        elif node.value.value == CONCAT:
            if node.left.value.nullable:
                node.value.firstPos = node.left.value.firstPos.union(
                    node.right.value.firstPos)
            else:
                node.value.firstPos = node.left.value.firstPos
            if node.right.value.nullable:
                node.value.lastPos = node.left.value.lastPos.union(
                    node.right.value.lastPos)
            else:
                node.value.lastPos = node.right.value.lastPos
        elif node.value.value == KLEENE_STAR:
            if node.right:
                node.value.firstPos = node.right.value.firstPos
                node.value.lastPos = node.right.value.lastPos
            else:
                node.value.firstPos = node.left.value.firstPos
                node.value.lastPos = node.left.value.lastPos
        else:
            node.value.firstPos = {node.value.id}
            node.value.lastPos = {node.value.id}

    def followPos(self, node: TreeNode):
        '''
        This function modifies the followPos attribute of the node.
        '''

        # If n is a cat-node with left child  c1 and right child c2, then every position i in lastpost(c1), all positions in firstpos(c2) are in followpos(i).
        if node.value.value == CONCAT:
            for i in node.left.value.lastPos:
                self.followPosDict[i] = self.followPosDict.get(i, set()).union(
                    node.right.value.firstPos)
        # if n is a star-node, and i is a position in lastpos(n), then all positions in firstpos(n) ar in followpos(i).
        elif node.value.value == KLEENE_STAR:
            for i in node.value.lastPos:
                self.followPosDict[i] = self.followPosDict.get(i, set()).union(
                    node.value.firstPos)
    '''
    ↑↑ END ALGORITHMS ↑↑
    '''

    def specialSimulate(self, input: list):
        '''
        This method simulates for recognize tokens in the input.
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
                for transition in self.transitions:
                    if transition.tail_id == statePointer and transition.using.startswith('#'):
                        # Return the transition using the '#' symbol
                        return transition.using[1:], idx
                return False, idx
        if transition.tail_id == statePointer and transition.using.startswith('#'):
            # Return the transition using the '#' symbol
            return transition.using[1:], idx
        self.simulationTime = time.perf_counter() - start_time
        return False, len(input)
