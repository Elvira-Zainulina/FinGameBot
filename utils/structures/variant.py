class Variant(object):
    def __init__(self, data: dict):
        self._answer = data["answer"]
        self._description = data["description"]

    def __repr__(self):
        return self._answer
