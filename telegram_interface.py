from connectivity_bot.telegram_wrapper import TelegramBot, TelegramMessageFormat, asynchandler
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from subprocess import STDOUT, check_output
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
    TelegramBot.add_handler(CommandHandler('diagnostics', diagnostics), description="Diagnostic")
    TelegramBot.add_handler(CommandHandler('cli', cli), description="Usage: cli <command>")


    TelegramBot.add_handler(MessageHandler(Filters.text, unknown_command))

    new_advert_format = TelegramMessageFormat('New advert found','',body_padding,'{}: {}')
    TelegramBot.add_format('new_advertisement',new_advert_format)

    format = TelegramMessageFormat('Help:','\n',body_padding,'/{}: {}')
    TelegramBot.add_format('help', format, constant_data=TelegramBot.command_desc)

    format = TelegramMessageFormat('Error occured:','\n','','{}')
    TelegramBot.add_format('error', format)


def start_telegram_bot():
    TelegramBot.updater.start_polling()
    TelegramBot.send_raw_message("Schiphol bot started")


def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def diagnostics(update: Update, context: CallbackContext):

    output = check_output("/home/pi/git/schiphol-recorder/scripts/diagnostics.sh", stderr=STDOUT, timeout=30)
    print(output.decode("utf-8"))
    update.message.reply_text(str(output.decode("utf-8")))
    return

def cli(update: Update, context: CallbackContext):
    try:
        if len(context.args) != 1:
            return
        
        command_arg = context.args[0]
        output = check_output(str(command_arg), stderr=STDOUT, timeout=30)
        print(output.decode("utf-8"))
        update.message.reply_text(str(output.decode("utf-8")))
    except Exception as e:
        logger.error(e, exc_info=True)
        update.message.reply_text(str(e))

    return