from utils import Bot, QuizSequence, UserProgress
from utils.filters import (FilterQuiz, FilterRound, FilterNothing,
                           FilterNone, FilterOthers, FilterMyStat)
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup


class FinGameBot(Bot):
    _user_stat = {}  # key - user id, value - user statistic (UserStatistic)
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
        others_filter = FilterOthers()
        mystat_filter = FilterMyStat()

        msg_quiz_handler = MessageHandler((~None_filter) & quiz_filter, self.quiz_start)
        self._dispatcher.add_handler(msg_quiz_handler)

        msg_round_handler = MessageHandler((~None_filter) & round_filter, self.round)
        self._dispatcher.add_handler(msg_round_handler)

        msg_others_handler = MessageHandler((~None_filter) & others_filter, self.check_others)
        self._dispatcher.add_handler(msg_others_handler)

        msg_mystat_handler = MessageHandler((~None_filter) & mystat_filter, self.my_stat)
        self._dispatcher.add_handler(msg_mystat_handler)

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

        others_handler = CommandHandler('others', self.check_others)
        self._dispatcher.add_handler(others_handler)

        mystat_handler = CommandHandler('mystat', self.my_stat)
        self._dispatcher.add_handler(mystat_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        self._dispatcher.add_handler(unknown_handler)

        self._dispatcher.add_handler(CallbackQueryHandler(self.quiz, pattern='quiz'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.check_answer_action, pattern='answer_\\d'))
        self._dispatcher.add_handler(CallbackQueryHandler(self.end, pattern='end'))

    @staticmethod
    def quiz_keyboard_variants(options: list):
        keyboard = []
        for i in range(len(options)):
            keyboard.append([InlineKeyboardButton(options[i], callback_data=f'answer_{i}')])
        keyboard.append([InlineKeyboardButton("Завершить игру", callback_data='end')])
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
                    [KeyboardButton("Олег, моя статистика")],
                    [KeyboardButton("Олег, как там у других")],
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
                   "/mystat - Олег, моя статистика \n" \
                   "/others - Олег, как там у других \n" \
                   "/round - Поиграть в Раунд с Олегом (not implemented)."
        context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg)

    def image(self, update, context):
        img_path = self._quiz_sequence.get_block(3).get_advice_pic()
        context.bot.send_photo(update.effective_chat.id,
                               photo=open(img_path, 'rb'))

    def start(self, update, context):
        cur_user = update.effective_chat
        self._user_stat[cur_user["id"]] = UserProgress(cur_user)
        greeting_username = " "
        if cur_user['username'] is not None:
            greeting_username += "@" + cur_user['username']
        else:
            greeting_username = ""

        hello_msg = f"Привет{greeting_username}!\n" \
                    "Я твой личный финансовый консультант Олег. " \
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

    def check_others(self, update, context):
        cur_user_id = update.effective_chat["id"]
        if len(self._user_stat) == 0 or (cur_user_id in self._user_stat.keys() and len(self._user_stat) == 1):
            context.bot.send_message(chat_id=update.effective_chat.id, text="Никого не вижу")
        else:
            message = "О, так ты играешь не один!\n" \
                      "C тобой играют твои следующие друзья (игрок: набрано очков/максимальное количество):\n"
            friends_score = {}
            n = 1
            for stat_key in self._user_stat.keys():
                if stat_key != cur_user_id:
                    username = self._user_stat[stat_key].get_username()
                    right, total = self._user_stat[stat_key].quiz_stat.get_score()
                    message += f"{n}. @{username}: {right}/{total}\n"
                    n += 1
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    def my_stat(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Не знаю")

    def quiz_start(self, update, context):
        update.message.reply_text("Ты готов испытать свои силы?",
                                  reply_markup=self.quiz_start_keyboard())

    def quiz(self, update, context):
        # remove keyboard from the previous cell
        query = update.callback_query
        context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                              message_id=query.message.message_id)

        # get user info & insert to stat
        cur_user = update.effective_chat
        if cur_user["id"] not in self._user_stat.keys():
            self._user_stat[cur_user["id"]] = UserProgress(cur_user)

        cur_block = self._user_stat[cur_user["id"]].quiz_stat.get_current_stage()
        cur_question = self._user_stat[cur_user["id"]].quiz_stat.get_current_question()
        print(self._user_stat[cur_user["id"]].get_username() + f" playing quiz({cur_block}:{cur_question})")

        # check if questions are over
        if cur_block >= self._quiz_sequence.get_sequence_size():
            self._user_stat[cur_user["id"]].quiz_stat.set_current_stage(0)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Новых вопросов нет. Готов ли ты к повторению?",
                                     reply_markup=self.quiz_start_keyboard())
            return

        # generate new question
        question_obj = self._quiz_sequence.get_question(cur_block, cur_question)
        self._user_stat[cur_user["id"]].set_question(question_obj)
        question = question_obj.get_text()
        options = question_obj.get_variants_answers()

        context.bot.send_message(chat_id=update.effective_chat.id, text=question,
                                 reply_markup=self.quiz_keyboard_variants(options))

    def update_cur_position(self, update, context):
        cur_user = update.effective_chat
        cur_block = self._user_stat[cur_user["id"]].quiz_stat.get_current_stage()
        cur_question = self._user_stat[cur_user["id"]].quiz_stat.get_current_question()
        block = self._quiz_sequence.get_block(cur_block)
        if cur_question < block.get_block_size() - 1:
            self._user_stat[cur_user["id"]].quiz_stat.set_current_question(cur_question + 1)
        else:
            advice = block.get_advice()
            picture = block.get_advice_pic()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=advice)
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=open(picture, 'rb'),
                                   reply_markup=self.quiz_cont_keyboard())

            self._user_stat[cur_user["id"]].quiz_stat.set_current_stage(cur_block + 1)
            self._user_stat[cur_user["id"]].quiz_stat.set_current_question(0)

    def generate_message_answer(self, cur_answer: int, cur_user_id):
        cur_block = self._user_stat[cur_user_id].quiz_stat.get_current_stage()
        cur_question = self._user_stat[cur_user_id].quiz_stat.get_current_question()

        question_obj = self._quiz_sequence.get_question(cur_block, cur_question)
        message = question_obj.get_text() + '\n'
        true_answers = question_obj.get_true()
        ans = question_obj.get_variants_answers()[cur_answer]
        exp = question_obj.get_variants_explanation()[cur_answer]
        is_correct = False
        if (cur_answer + 1) in true_answers:
            message += f'\nВаш ответ: {ans}. \n\n 🎉 🎉 🎉Совершенно верно! {exp}'
            is_correct = True
        else:
            message += f'\n🙈 К сожалению, ответ "{ans}" неправильный. \n\n' + f'Объяснение: {exp}'
        return message, is_correct

    def check_answer_action(self, update, context):
        cur_answer_num = int(str(update['callback_query']['data']).split("answer_")[-1])
        cur_user = update.effective_chat
        answer, is_correct = self.generate_message_answer(cur_answer_num, cur_user["id"])
        self._user_stat[cur_user["id"]].quiz_stat.increase_right(is_correct)
        self._user_stat[cur_user["id"]].quiz_stat.increase_total()
        self.print_question_answer(update, context, answer)

    def print_question_answer(self, update, context, answer):
        self.update_cur_position(update, context)
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=answer,
                                      reply_markup=self.quiz_next_keyboard())

    def end(self, update, context):
        self._cur_question = 0
        query = update.callback_query
        context.bot.send_message(chat_id=query.message.chat_id,
                                 text="Буду ждать новой игры")
