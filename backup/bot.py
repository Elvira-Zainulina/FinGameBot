from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Poll, ForceReply


updater = Updater(token='1168824743:AAEczB0ToLlw-TIHhuQivVaSvHN3OisufMI', use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def quiz_keyboard(options, right_answer):
    answers = ['right' if right_answer == i else 'wrong' for i in range(4)]
    keyboard = [[InlineKeyboardButton(options[0], callback_data=answers[0]),
                 InlineKeyboardButton(options[1], callback_data=answers[1])],
                [InlineKeyboardButton(options[2], callback_data=answers[2]),
                 InlineKeyboardButton(options[3], callback_data=answers[3])],
                [InlineKeyboardButton("Завершить игру", callback_data='end')]]
    return InlineKeyboardMarkup(keyboard)


def quiz_start_keyboard():
    keyboard = [[InlineKeyboardButton("Да, готов", callback_data='quiz')],
                [InlineKeyboardButton("Нет, не готов", callback_data='end')]]
    return InlineKeyboardMarkup(keyboard)


def quiz_next_keyboard():
    keyboard = [[InlineKeyboardButton("Следующий вопрос", callback_data='quiz')],
                [InlineKeyboardButton("Завершить игру", callback_data='end')]]
    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def quiz_start(update, context):
    update.message.reply_text("Ты готов испытать свои силы?",
                              reply_markup=quiz_start_keyboard())


def quiz(update, context):
    question = 'Questions'
    options = ['Ans1', 'Ans2', 'Ans3', 'Ans4']
    right_answer = 0

    query = update.callback_query
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=question,
                                  reply_markup=quiz_keyboard(options, right_answer))


def right(update, context):
    congrats = 'Congrats. Explanation.'
    query = update.callback_query
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=congrats,
                                  reply_markup=quiz_next_keyboard())


def wrong(update, context):
    explanation = 'Explanation.'

    query = update.callback_query
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=explanation,
                                  reply_markup=quiz_next_keyboard())
    # context.bot.send_message(chat_id=update.effective_chat.id, text=explanation)


def end(update, context):
    query = update.callback_query
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text="Буду ждать нового раунда")

# def quiz(update, context):
#     keyboard = [['Ans1', 'Ans2'], ["Ans3", "Ans4"]]
#
#     question = "Question."
#     explanation = 'Explanation.'
#
#     reply_markup = ReplyKeyboardMarkup(keyboard,
#                                        one_time_keyboard=True,
#                                        resize_keyboard=True)
#     context.bot.sendPoll(chat_id=update.effective_chat.id,
#                          question=question,
#                          options=['Ans1', 'Ans2', "Ans3", "Ans4"],
#                          type=Poll.QUIZ, correct_option_id=0,
#                          expanation=explanation, reply_markup = ForceReply())


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

quiz_handler = CommandHandler('quiz', quiz_start)
dispatcher.add_handler(quiz_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

dispatcher.add_handler(CallbackQueryHandler(quiz, pattern='quiz'))
dispatcher.add_handler(CallbackQueryHandler(right, pattern='right'))
dispatcher.add_handler(CallbackQueryHandler(wrong, pattern='wrong'))
dispatcher.add_handler(CallbackQueryHandler(end, pattern='end'))


if __name__ == '__main__':
    updater.start_polling()
