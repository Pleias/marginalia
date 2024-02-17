class data_entity:
    def __init__(self, field = None, definition = None, choice=None, min_length = None, literal_check = False):
        self.field = field
        self.definition = definition
        self.choice = choice
        self.min_length = min_length
        self.literal_check = literal_check
