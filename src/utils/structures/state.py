class State(object):
    '''
    State class for a state in a finite automaton
    '''

    def __init__(self, value, id=None, initial=False, acceptance=False):
        self.value = value
        self.marked = False
        self.id = id
        self.acceptance = acceptance
        self.initial = initial

    def copy(self):
        return State(self.value, self.id, self.initial, self.acceptance)

    def __str__(self) -> str:
        return f'{self.id} {self.value} {self.initial} {self.acceptance}'
