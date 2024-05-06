class TreeNode(object):
    '''
    Node class for a binary tree data structure
    '''

    def __init__(self, value, right=None, left=None):
        self.value = value
        self.right = right
        self.left = left

    def __str__(self):
        return str(self.value)

    def postOrderTraversal(self, function: callable = None):
        '''
        Post order traversal of the binary tree for applying a function to each node
        Parameters:
        - function: A function to be applied to each node of the binary tree.
        '''
        if self.left:
            self.left.postOrderTraversal(function)
        if self.right:
            self.right.postOrderTraversal(function)
        if function:
            function(self)

    def deepCopy(self):
        '''
        Deep copy of the binary tree.
        '''
        if self.left:
            left = self.left.deepCopy()
        else:
            left = None
        if self.right:
            right = self.right.deepCopy()
        else:
            right = None
        return TreeNode(self.value, right, left)

    def getPlainRepresentation(self):
        '''
        Returns a plain representation of the binary tree.
        '''
        plainRepresentation = []
        self.postOrderTraversal(
            lambda node: plainRepresentation.append(node.value))
        return plainRepresentation


"""
@Reference: https://www.tutorialspoint.com/python_data_structure/python_binary_tree.htm
"""
