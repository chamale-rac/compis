"""
@File name: _ast.py
@Module: AbstractSyntaxTree
@Author: Samuel Chamalé
@Date: 31/01/2024
@Description:  This file contains the implementation of the AbstractSyntaxTree class.
"""


from src.utils.constants import KLEENE_STAR, OR, CONCAT, ZERO_OR_ONE, ONE_OR_MORE, EPSILON
from src.utils.structures.tree_node import TreeNode
from src.utils.tools import errorsManager
from graphviz import Digraph


class AbstractSyntaxTree(object):
    '''
    This class represents the abstract syntax tree of a regular expression.
    '''

    def __init__(self, postfixRegEx: list):
        '''
        This is the constructor of the class. 
        Parameters:
        - postfixRegEx: A regular expression in postfix notation.
        '''
        self.errorsManager = errorsManager()
        self.alphabet: set[str] = set()
        self.root: TreeNode = self.PE2AS(
            postfixRegEx)
        self.alphabet = sorted(list(self.alphabet))

    '''
    ↓↓ ALGORITHMS ↓↓
    '''

    def PE2AS(self, postfixRegEx: list) -> TreeNode:
        '''
        Postfix Expression to Abstract Syntax Tree algorithm implementation.
        Parameters:
        - postfixRegEx: A regular expression in postfix notation.
        Returns:
        - The root of the abstract syntax tree of the regular expression.
        '''
        stack: list[TreeNode] = []

        for c in postfixRegEx:
            if c == KLEENE_STAR:
                if not stack:
                    self.errorsManager.addError(
                        'There is no character to apply the Kleene star to', 'Invalid regular expression'
                    )
                    return None
                stack.append(TreeNode(c, stack.pop()))
            elif c in [OR, CONCAT]:
                if len(stack) < 2:
                    self.errorsManager.addError(
                        f'There are not enough characters to apply {c} to', 'Invalid regular expression'
                    )
                    return stack.pop()
                stack.append(TreeNode(c, stack.pop(), stack.pop()))
            elif c == ZERO_OR_ONE:
                if not stack:
                    self.errorsManager.addError(
                        'There is no character to apply the zero or one to', 'Invalid regular expression'
                    )
                    return None
                stack.append(TreeNode(OR, stack.pop(), TreeNode(EPSILON)))
            elif c == ONE_OR_MORE:
                if not stack:
                    self.errorsManager.addError(
                        'There is no character to apply the one or more to', 'Invalid regular expression'
                    )
                    return None
                peaked = stack.pop()
                stack.append(TreeNode(CONCAT, TreeNode(
                    KLEENE_STAR, peaked), peaked.deepCopy()))
            else:
                stack.append(TreeNode(c))
                if c != EPSILON:
                    self.alphabet.add(c)

        return stack.pop()
    '''
    ↑↑ END ALGORITHMS ↑↑
    '''

    def draw(self, name: str, id_: int | str, label: str = None, cast: bool = False):
        '''
        This method is made for drawing the abstract syntax tree.
        '''
        dot = Digraph(
            graph_attr={
                'rankdir': 'TB',
            }
        )

        dot.attr(label=label)

        def add_nodes_edges(tree_node, parent_id=None):
            # Base case: if the tree node is None, return
            if tree_node is None:
                return

            # Create a unique id for the current node
            node_id = id(tree_node)

            # Add the current node to the graph
            # try converting the tree_node.value to int
            label = ''
            if cast:
                try:
                    label = chr(int(tree_node.value))
                except:
                    label = tree_node.value
            else:
                label = tree_node.value

            dot.node(str(node_id), label=label)

            # If this is not the root node, add an edge from the parent node to the current node
            if parent_id is not None:
                dot.edge(str(parent_id), str(node_id))

            # Recurse on the left and right children
            add_nodes_edges(tree_node.left, node_id)
            add_nodes_edges(tree_node.right, node_id)

        # Start the recursion from the root
        add_nodes_edges(self.root)

        dot.render(f'output/{id_}/{name}', format='png', cleanup=True)
