from typing import List

from utils.structures import Question


class QuizBlock(object):
    def __init__(self, data: dict):
        self._id = data["id"]
        self._advice = data["advice"]
        self._pic_advice = data["pic"]
        self._questions = List[Question]
        for q in data["data"]:
            self._questions.append(Question(q))
