from utils.structures import QuizBlock
from typing import List
import json


class QuizSequence(object):
    def __init__(self, path: str):
        self._path = path

        self._blocks = []
        self.read_data()

    def read_data(self):
        with open(self._path, encoding='utf-8') as read_file:
            data = json.load(read_file)
            for block in data:
                self._blocks.append(QuizBlock(block))

    def get_block(self, block_id: int) -> QuizBlock:
        if len(self._blocks) > block_id >= 0:
            return self._blocks[block_id]
        elif self.get_block_count() > 0:
            return self._blocks[0]

    def get_block_count(self) -> int:
        return len(self._blocks)
