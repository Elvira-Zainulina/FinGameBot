from utils.structures import Question


class QuestionGenerator(object):
    def __init__(self, key: str, data: list):
        self._type = key
        self._blocks = []
        for block in data:
            cur_block = []
            for qa in block:
                cur_block.append(Question(qa))
            self._blocks.append(cur_block)
