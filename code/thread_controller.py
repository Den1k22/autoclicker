

class ThreadController:

    def __init__(self):
        self.work = False

    def is_working(self):
        return self.work

    def change_state(self, state):
        self.work = state
