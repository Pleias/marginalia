#The class for each entry in the data scheme.
class data_entity:
    def __init__(self, field = None, type_field = None, definition = None, choice=None, min_length = None, literal_check = False):
        self.field = field
        self.definition = definition
        self.type_field = type_field
        self.choice = choice
        self.min_length = min_length
        self.literal_check = literal_check
