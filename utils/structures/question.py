from .variant import Variant


class Question:
    def __init__(self, data: dict):
        self._question = data["question"]
        self._variants = self._get_variants(data["variants"])
        self._true_variant = data["true_variant"]

    @staticmethod
    def _get_variants(data: list):
        variants = []
        for var in data:
            variants.append(Variant(var))
        return variants

    def get_text(self):
        return self._question

    def get_true(self):
        return self._true_variant

    def get_vars(self):
        text_vars = []
        for var in self._variants:
            text_vars.append(var._answer)
        return text_vars

    def __repr__(self):
        return "Q: {q}, true: {t}".format(q=self._question, t=self._true_variant)
