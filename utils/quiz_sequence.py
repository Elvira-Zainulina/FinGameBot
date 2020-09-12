from utils.structures import QuizBlock
from typing import List


class QuizSequence(object):
    def __init__(self, data: list):
        self._blocks = List[QuizBlock]

    def read_data(self, data: list):
        for block in data:
            self._blocks.append(QuizBlock(block))
