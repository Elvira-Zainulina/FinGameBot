from telegram.ext import BaseFilter
# rules to be corrected


class FilterQuiz(BaseFilter):
    def filter(self, message):
        return 'quiz' in message.text.lower() or 'квиз' in message.text.lower()


class FilterRound(BaseFilter):
    def filter(self, message):
        return 'round' in message.text.lower() or 'раунд' in message.text.lower()


class FilterNothing(BaseFilter):
    def filter(self, message):
        return 'не хочу' in message.text.lower()


class FilterNone(BaseFilter):
    def filter(self, message):
        return message.text is None


class FilterOthers(BaseFilter):
    def filter(self, message):
        return 'олег, как там у других' in message.text.lower() or \
            'проверить остальных' in message.text.lower() or \
            'check others' in message.text.lower()
