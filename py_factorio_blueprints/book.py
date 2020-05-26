

class Book:
    def __init__(self, data, **kwargs):
        self.name = 'blueprint-book'
        self.label = ''
        self.label_color = None
        self.blueprints = []
        self.active_index = 0
        self.version = 0
