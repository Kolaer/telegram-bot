"""
Связь бота непосредственно с Телеграм посредством Telegram API. Используется Shelve -- "словареобразная" база данных  
для данных каждого пользователя.
"""
import logging
import shelve

from telegram.ext import Updater, MessageHandler, Filters

from src.calc import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

fo = open("telegram_token", "r")

updater = Updater(fo.readline())

fo.close()

with shelve.open("MySuperCoolDataBase", writeback=True) as envs:
    def text_handler(bot, update):
        """Обработчик сообщений"""
        chat_id = update.message.chat_id
        s_chat_id = str(chat_id)

        if s_chat_id not in envs:
            data = Environment().get_data()
            envs[s_chat_id] = data

        text = update.message.text

        try:
            data = envs[s_chat_id]
            env_calc = Environment()
            env_calc.set_data(data)

            res = str(calculate(text, env_calc))

            envs[s_chat_id] = env_calc.get_data()
        except RuntimeError as e:
            res = str(e.args)

        bot.sendMessage(chat_id=chat_id, text=res)
        envs.sync()


    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))

    updater.start_polling()
    updater.idle()
