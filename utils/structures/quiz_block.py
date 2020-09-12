from typing import List

from utils.structures import Question


class QuizBlock(object):
    def __init__(self, data: dict):
        self._id = data["id"]
        self._advice = data["advice"]
        self._pic_advice = data["pic"]
        self._questions = self.read_questions(data["data"])

    @staticmethod
    def read_questions(data: list) -> List[Question]:
        questions = []
        for q in data:
            questions.append(Question(q))
        return questions

    def __repr__(self):
        return "Block {id}. Advice: {advice}".format(id=self._id, advice=self._advice)

    def get_block_size(self) -> int:
        return len(self._questions)

    def get_question(self, question_id: int) -> Question:
        if self.get_block_size() > question_id >= 0:
            return self._questions[question_id]
        elif self.get_block_size() > 0:
            return self._questions[0]

    def get_advice(self) -> str:
        return self._advice

    def get_advice_pic(self) -> str:
        return self._pic_advice
