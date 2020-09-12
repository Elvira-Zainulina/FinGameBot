from typing import List

from utils.structures import Question


class RoundBlock(object):
    def __init__(self, data: dict):
        self._level = data["level"]
        self._questions = List[Question]
        for q in data["data"]:
            self._questions.append(Question(q))
