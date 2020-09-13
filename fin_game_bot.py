from utils import Bot, QuizSequence
from utils.filters import FilterQuiz, FilterRound, FilterNothing, FilterNone
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup


class FinGameBot(Bot):
    _quiz_sequence = None
    _round_sequence = None

    _cur_question = 0
    _cur_block = 0

    def __init__(self, bot_token: str):
        super(FinGameBot, self).__init__(bot_token)
        self._quiz_sequence = QuizSequence("data/quiz_data.json")

    def append_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self._dispatcher.add_handler(start_handler)

        quiz_filter = FilterQuiz()
        round_filter = FilterRound()
        non_filter = FilterNothing()
        None_filter = FilterNone()

        msg_quiz_handler = MessageHandler((~None_filter) & quiz_filter, self.quiz_start)
        self._dispatcher.add_handler(msg_quiz_handler)

        msg_round_handler = MessageHandler((~None_filter) & round_filter, self.round)
        self._dispatcher.add_handler(msg_round_handler)

        echo_handler = MessageHandler((~None_filter) & Filters.text & (~Filters.command) & (~non_filter) &
                                      (~quiz_filter) & (~round_filter), self.unknown)
        self._dispatcher.add_handler(echo_handler)

        quiz_handler = CommandHandler('quiz', self.quiz_start)
        self._dispatcher.add_handler(quiz_handler)

        round_handler = CommandHandler('round', self.round)
        self._dispatcher.add_handler(round_handler)

        help_handler = CommandHandler('help', self.help)
        self._dispatcher.add_handler(help_handler)

        image_handler = CommandHandler('image', self.image)
        self._dispatcher.add_handler(image_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        self._dispatcher.add_handler(unknown_handler)

        self._dispatcher.add_handler(CallbackQueryHandler(self.quiz, pattern='quiz'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.right, pattern='right'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.wrong, pattern='wrong'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.end, pattern='end'))

    @staticmethod
    def quiz_keyboard4(options, right_answer):
        answers = ['right' if (right_answer - 1) == i else 'wrong' for i in range(4)]
        keyboard = [[InlineKeyboardButton(options[0], callback_data=answers[0]),
                     InlineKeyboardButton(options[1], callback_data=answers[1])],
                    [InlineKeyboardButton(options[2], callback_data=answers[2]),
                     InlineKeyboardButton(options[3], callback_data=answers[3])],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_keyboard2(options, right_answer):
        answers = ['right' if (i + 1) in right_answer else 'wrong' for i in range(2)]
        keyboard = [[InlineKeyboardButton(options[0], callback_data=answers[0])],
                    [InlineKeyboardButton(options[1], callback_data=answers[1])],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_start_keyboard():
        keyboard = [[InlineKeyboardButton("Да, готов", callback_data='quiz')],
                    [InlineKeyboardButton("Нет, не готов", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_cont_keyboard():
        keyboard = [[InlineKeyboardButton("Продолжить игру", callback_data='quiz')],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_help_keyboard():
        keyboard = [[KeyboardButton("Олег, давай поиграем в quiz")],
                    [KeyboardButton("Олег, я хочу поиграть в Раунд")],
                    [KeyboardButton("Я не хочу играть.")]]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    @staticmethod
    def quiz_next_keyboard():
        keyboard = [[InlineKeyboardButton("Следующий вопрос", callback_data='quiz')],
                    [InlineKeyboardButton("Завершить игру", callback_data='end')]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help(update, context):
        help_msg = "/quiz - Поиграть в квиз с Олегом, \n" \
                   "/round - Поиграть в Раунд с Олегом."
        context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg)

    def image(self, update, context):
        img_path = self._quiz_sequence.get_block(3).get_advice_pic()
        context.bot.send_photo(update.effective_chat.id,
                               photo=open(img_path, 'rb'))

    def start(self, update, context):
        hello_msg = "Я твой личный финансовый консультант Олег. " \
                    "Я помогу разобраться в принципах финансовой грамотности и " \
                    "покажу, как ты запросто сможешь применять их на практике."
        context.bot.send_message(chat_id=update.effective_chat.id, text=hello_msg,
                                 reply_markup=self.quiz_help_keyboard())

    def unknown(self, update, context):
        msg = "Давай лучше поиграем в квиз или Раунд?"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                                 reply_markup=self.quiz_help_keyboard())

    @staticmethod
    def round(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not implemented error")

    def quiz_start(self, update, context):
        update.message.reply_text("Ты готов испытать свои силы?",
                                  reply_markup=self.quiz_start_keyboard())

    def quiz(self, update, context):
        test = self._quiz_sequence
        if self._cur_block > self._quiz_sequence.get_sequence_size():
            self._cur_block = 0
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Новых вопросов нет. Готов ли ты к повторению?",
                                     reply_markup=self.quiz_start_keyboard())
            return

        question_obj = test.get_question(self._cur_block, self._cur_question)
        question = question_obj.get_text()
        options = question_obj.get_variants_answers()
        right_answer = question_obj.get_true()

        context.bot.send_message(chat_id=update.effective_chat.id, text=question,
                                 reply_markup=self.quiz_keyboard2(options, right_answer))

    def update_cur_position(self, update, context):
        block = self._quiz_sequence.get_block(self._cur_block)
        if self._cur_question < block.get_block_size() - 1:
            self._cur_question += 1
        else:
            advice = block.get_advice()
            picture = block.get_advice_pic()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=advice)
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=open(picture, 'rb'),
                                   reply_markup=self.quiz_cont_keyboard())
            self._cur_block += 1
            self._cur_question = 0

    # TODO universal func for right/not right
    def generate_answer(self, is_right=True):
        question_obj = self._quiz_sequence.get_question(self._cur_block, self._cur_question)
        message = question_obj.get_text() + '\n'
        cur_answer = question_obj.get_true()[0] - 1
        ans = question_obj.get_variants_answers()[cur_answer] # TODO cur answer should be from real answer :(
        exp = question_obj.get_variants_explanation()[cur_answer]

        if is_right:
            message += f'\nВаш ответ: {ans}. \n\n 🎉 🎉 🎉Совершенно верно! {exp}'
        else:
            message += f'\n🙈 К сожалению, ответ "{ans}" неправильный. \n\n' + f'Объяснение: {exp}'
        return message

    def right(self, update, context):
        question_obj = self._quiz_sequence.get_question(self._cur_block, self._cur_question)
        congrats = question_obj.get_text() + '\n'
        cur_answer = question_obj.get_true()[0] - 1
        ans = question_obj.get_variants_answers()[cur_answer]
        exp = question_obj.get_variants_explanation()[cur_answer]
        congrats += f'\nВаш ответ: {ans}. \n\n 🎉 🎉 🎉Совершенно верно! {exp}'
        # self._story.append([question_obj.get_text(),
        #                     question_obj.get_vars()[question_obj.get_true()]])
        self.update_cur_position(update, context)
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=congrats,
                                      reply_markup=self.quiz_next_keyboard())

    def wrong(self, update, context):
        question_obj = self._quiz_sequence.get_question(self._cur_block, self._cur_question)
        explanation = question_obj.get_text() + '\n'
        cur_answer = question_obj.get_true()[0] % 2 # TODO it is stupid
        ans = question_obj.get_variants_answers()[cur_answer]
        exp = question_obj.get_variants_explanation()[cur_answer]
        explanation += f'\n🙈 К сожалению, ответ "{ans}" неправильный. \n\n' + f'Объяснение: {exp}'

        self.update_cur_position(update, context)
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=explanation,
                                      reply_markup=self.quiz_next_keyboard())

    @staticmethod
    def end(update, context):
        query = update.callback_query
        context.bot.send_message(chat_id=query.message.chat_id,
                                 text="Буду ждать новой игры")
