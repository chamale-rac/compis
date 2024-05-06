class SLR1(object):
    def __init__(self, lr0) -> None:
        self.lr0 = lr0
        self.action = {}
        self.goto = {}

        self.construct_tables()

    def construct_tables(self):
        pass
