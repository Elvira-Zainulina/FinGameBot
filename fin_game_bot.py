from utils.template_bot import Bot
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Poll, ForceReply
import os
import json


class FinGameBot(Bot):
    quiz_data_ = None

    def __init__(self, bot_token: str, data_pth: str):
        super(FinGameBot, self).__init__(bot_token, data_pth)

        print(self._bot_token)
        self.read_data("quiz")

    def read_data(self, key: str):
        print(key)
        with open(self._data_pth) as read_file:
            data = json.load(read_file)
            print(data)

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
    def quiz_keyboard(options, right_answer):
        answers = ['right' if right_answer == i else 'wrong' for i in range(4)]
        keyboard = [[InlineKeyboardButton(options[0], callback_data=answers[0]),
                     InlineKeyboardButton(options[1], callback_data=answers[1])],
                    [InlineKeyboardButton(options[2], callback_data=answers[2]),
                     InlineKeyboardButton(options[3], callback_data=answers[3])],
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
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    @staticmethod
    def echo(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    @staticmethod
    def caps(update, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

    @staticmethod
    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def quiz_start(self, update, context):
        update.message.reply_text("Ты готов испытать свои силы?",
                                  reply_markup=self.quiz_start_keyboard())

    def quiz(self, update, context):
        question = 'Questions'
        options = ['Ans1', 'Ans2', 'Ans3', 'Ans4']
        right_answer = 0

        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=question,
                                      reply_markup=self.quiz_keyboard(options, right_answer))

    def right(self, update, context):
        congrats = 'Congrats. Explanation.'
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=congrats,
                                      reply_markup=self.quiz_next_keyboard())

    def wrong(self, update, context):
        explanation = 'Explanation.'

        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=explanation,
                                      reply_markup=self.quiz_next_keyboard())

    @staticmethod
    def end(update, context):
        query = update.callback_query
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text="Буду ждать нового раунда")
