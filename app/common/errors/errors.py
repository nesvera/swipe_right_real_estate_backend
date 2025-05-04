class DeserializationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"{errors}")

class SerializationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"{errors}")