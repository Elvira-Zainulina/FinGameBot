from utils.structures import RoundBlock
from typing import List
import json


class RoundSequence(object):
    def __init__(self, path: str):
        self._path = path

        self._blocks = List[RoundBlock]
        self.read_data()

    def read_data(self):
        with open(self._path, encoding='utf-8') as read_file:
            data = json.load(read_file)
            for block in data:
                self._blocks.append(RoundBlock(block))
