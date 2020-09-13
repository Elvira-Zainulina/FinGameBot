from telegram.chat import Chat

from utils.structures import Question


class Statistic(object):
    def __init__(self):
        self._right_answered = 0
        self._total_answered = 0
        self._current_question = 0
        self._current_stage = 0

    def increase_right(self):
        self._right_answered += 1

    def increase_total(self):
        self._total_answered += 1

    def get_score(self):
        return self._right_answered, self._total_answered

    def get_current_question(self):
        return self._current_question

    def set_current_question(self, value: int):
        self._current_question = value

    def get_current_stage(self):
        return self._current_stage

    def set_current_stage(self, value: int):
        self._current_stage = value


class UserProgress(object):
    def __init__(self, user_info: Chat):
        self._user_info = user_info
        self._current_question = None
        self.quiz_stat = Statistic()
        self.round_stat = Statistic()

    def get_username(self):
        return self._user_info.username

    def set_question(self, question: Question):
        self._current_question = question

    def get_question(self):
        return self._current_question
