from telegram.ext import Updater, MessageHandler, Filters

from calc import *

fo = open("telegram_token", "r")

updater = Updater(fo.readline())

fo.close()

envs = dict()


def text_handler(bot, update):
    chat_id = update.message.chat_id
    if chat_id not in envs:
        envs[chat_id] = Environment()

    text = update.message.text

    try:
        res = str(calculate(text, envs[chat_id]))
    except RuntimeError as e:
        res = str(e.args)

    bot.sendMessage(chat_id=chat_id, text=res)


updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))

updater.start_polling()
updater.idle()