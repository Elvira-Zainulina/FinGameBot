from telegram.ext import BaseFilter


class FilterQuiz(BaseFilter):
    def filter(self, message):
        return 'quiz' in message.text.lower() or 'квиз' in message.text.lower()  # very stupid rule


class FilterRound(BaseFilter):
    def filter(self, message):
        return 'round' in message.text.lower() or 'раунд' in message.text.lower()  # very stupid rule


class FilterNothing(BaseFilter):
    def filter(self, message):
        return 'не хочу' in message.text.lower()  # very stupid rule
