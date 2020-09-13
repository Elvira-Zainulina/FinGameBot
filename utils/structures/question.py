from .variant import Variant
from typing import List


class Question:
    def __init__(self, data: dict):
        self._question = data["question"]
        self._variants = self._get_variants_from_data(data["variants"])
        self._true_variant = data["true_variant"]

    @staticmethod
    def _get_variants_from_data(data: list) -> List[Variant]:
        variants = []
        for var in data:
            variants.append(Variant(var))
        return variants

    def get_text(self) -> str:
        return self._question

    def get_true(self) -> int:
        return self._true_variant

    def get_variants_answers(self):
        text_vars = []
        for var in self._variants:
            text_vars.append(var.get_variant_answer())
        return text_vars

    def get_variants_explanation(self):
        text_vars = []
        for var in self._variants:
            text_vars.append(var.get_variant_description())
        return text_vars

    def __repr__(self):
        return "Q: {q}, true: {t}".format(q=self._question, t=self._true_variant)
