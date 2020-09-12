class UserProgress(object):
    def __init__(self, user_id):
        self._user_id = user_id
        self._current_quiz_question = 0
        self._current_quiz_stage = 0
        self._current_question = None

