class Variant(object):
    def __init__(self, data: dict):
        self._answer = data["answer"]
        self._description = data["description"]

    def get_variant_answer(self) -> str:
        return self._answer

    def get_variant_description(self) -> str:
        return self._description

    def __repr__(self):
        return self._answer
