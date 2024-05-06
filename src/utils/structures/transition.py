class Transition(object):
    '''
    Transition class for a transition in a finite automaton 
    '''

    def __init__(self, tail_id, head_id, using) -> None:
        self.tail_id = tail_id
        self.head_id = head_id
        self.using = using

    def __str__(self) -> str:
        return f'{self.tail_id} {self.using} {self.head_id}'
