from utils import Bot, QuestionGenerator

from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json


class FinGameBot(Bot):
    _users_progress = {}
    _quiz_data = None
    _cur_question = 0

    def __init__(self, bot_token: str, data_pth: str):
        super(FinGameBot, self).__init__(bot_token, data_pth)
        self._quiz_data = self.read_data("quiz")

    def read_data(self, key: str):
        with open(self._data_pth, encoding='utf-8') as read_file:
            data = json.load(read_file)
            return QuestionGenerator(key, data[key])

    def append_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self._dispatcher.add_handler(start_handler)

        echo_handler = MessageHandler(Filters.text & (~Filters.command), self.echo)
        self._dispatcher.add_handler(echo_handler)

        caps_handler = CommandHandler('caps', self.caps)
        self._dispatcher.add_handler(caps_handler)

        quiz_handler = CommandHandler('quiz', self.quiz_start)
        self._dispatcher.add_handler(quiz_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        self._dispatcher.add_handler(unknown_handler)

        self._dispatcher.add_handler(CallbackQueryHandler(self.quiz, pattern='quiz'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.right, pattern='right'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.wrong, pattern='wrong'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.end, pattern='end'))

    @staticmethod
    def quiz_keyboard4(options, right_answer):
        answers = ['right' if right_answer == i else 'wrong' for i in range(4)]
        keyboard = [[InlineKeyboardButton(options[0], callback_data=answers[0]),
                     InlineKeyboardButton(options[1], callback_data=answers[1])],
                    [InlineKeyboardButton(options[2], callback_data=answers[2]),
                     InlineKeyboardButton(options[3], callback_data=answers[3])],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_keyboard2(options, right_answer):
        answers = ['right' if right_answer == i else 'wrong' for i in range(2)]
        keyboard = [[InlineKeyboardButton(options[0], callback_data=answers[0]),
                     InlineKeyboardButton(options[1], callback_data=answers[1])],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)


    @staticmethod
    def quiz_start_keyboard():
        keyboard = [[InlineKeyboardButton("Да, готов", callback_data='quiz')],
                    [InlineKeyboardButton("Нет, не готов", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_next_keyboard():
        keyboard = [[InlineKeyboardButton("Следующий вопрос", callback_data='quiz')],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Привет! Я твой личный финансовый консультант Олег. Я помогу разобраться в "
                                      "принципах финансовой грамотности и покажу, как ты запросто сможешь применять "
                                      "их на практике. Чтобы узнать, как прямо сейчас ты можешь зарабатывать "
                                      "больше, а тратить меньше проходи Квиз! Если хочешь помериться знаниями"
                                      " с друзьями, приглашай их на Раунд!")

    @staticmethod
    def echo(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    @staticmethod
    def caps(update, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

    @staticmethod
    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Что за дичь?).")

    def quiz_start(self, update, context):
        update.message.reply_text("Ты готов испытать свои силы?",
                                  reply_markup=self.quiz_start_keyboard())

    def quiz(self, update, context):
        chat_instance = update["callback_query"]["chat_instance"]
        # if self._users_progress[chat_instance] is None:
        #     print("new user")
        #     self._users_progress[chat_instance] = {}
        #     self._users_progress[chat_instance]["cur_question"] = 0
        test = self._quiz_data._blocks[0]
        query = update.callback_query
        # test = self._quiz_data
        if self._cur_question >= len(test):
            self._cur_question = 0
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Новых вопросов нет. Готов ли ты к повторению?",
                                     reply_markup=self.quiz_start_keyboard())
            return

        question_obj = test[self._cur_question]
        question = question_obj.get_text()
        options = question_obj.get_vars()
        right_answer = question_obj.get_true()
        self._cur_question += 1

        context.bot.send_message(chat_id=update.effective_chat.id, text=question,
                                 reply_markup=self.quiz_keyboard2(options, right_answer))

    def right(self, update, context):
        question_obj = self._quiz_data._blocks[0][self._cur_question - 1]
        congrats = question_obj.get_text() + '\n'
        ans = question_obj.get_vars()[question_obj.get_true() % 2]
        congrats += f'Правильно. {ans}. Explanation.'
        # self._story.append([question_obj.get_text(),
        #                     question_obj.get_vars()[question_obj.get_true()]])
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=congrats,
                                      reply_markup=self.quiz_next_keyboard())

    def wrong(self, update, context):
        question_obj = self._quiz_data._blocks[0][self._cur_question - 1]
        explanation = question_obj.get_text() + '\n'
        ans = question_obj.get_vars()[question_obj.get_true() % 2]
        explanation += f'К сожалению, ответ "{ans}" неправильный. \n' + 'Explanation.'
        # self._story.append([question_obj.get_text(),
        #                     question_obj.get_vars()[question_obj.get_true() % 2]])
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=explanation,
                                      reply_markup=self.quiz_next_keyboard())

    @staticmethod
    def end(self, update, context):
        # df = pd.DataFrame(self._story, columns=['Question', 'Answer'])
        # df.to_csv(os.path.join('./logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.csv'))
        # self._story = []
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text="Буду ждать нового раунда")
