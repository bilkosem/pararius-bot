from connectivity_bot.telegram_wrapper import TelegramBot, TelegramMessageFormat, asynchandler
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

import logging

logger = logging.getLogger('pararius')

def init_telegram_bot(token, chat_id):
    desc_padding = '                '
    body_padding = '\n        '

    TelegramBot.setToken(token)
    TelegramBot.setChatId(chat_id)
    TelegramBot.add_handler(CommandHandler('kill', TelegramBot.kill), description="Killing the bot...")
    TelegramBot.add_handler(CommandHandler('help', TelegramBot.help), description="Print help message")
    TelegramBot.add_handler(CommandHandler('ping', TelegramBot.pong), description="Ping the bot")
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown_command))

    new_advert_format = TelegramMessageFormat('New advert found','',body_padding,'{}: {}')
    TelegramBot.add_format('new_advertisement',new_advert_format)

    format = TelegramMessageFormat('Help:','\n',body_padding,'/{}: {}')
    TelegramBot.add_format('help', format, constant_data=TelegramBot.command_desc)

    format = TelegramMessageFormat('Error occured:','\n','','{}')
    TelegramBot.add_format('error', format)


def start_telegram_bot():
    TelegramBot.updater.start_polling()
    TelegramBot.send_raw_message("Pararius bot started")


def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)
