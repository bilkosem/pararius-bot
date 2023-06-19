import time
from connectivity_bot.telegram_wrapper import *
import os
import signal
import telegram_interface
import itertools

is_bot_enabled = True

def application():

    time.sleep(1)
    
    return  


if __name__ == "__main__":

    f = open(str(sys.argv[1]),'r')
    main_config = json.load(f)


    f = open(main_config['telegram_config'],'r')
    telegram_config = json.load(f)

    telegram_interface.init_telegram_bot(telegram_config['token'], telegram_config['chat_id'])
    telegram_interface.start_telegram_bot()


    while(True):
        
        try:
            if not is_bot_enabled:
                continue

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            application()

        except Exception as e:
            print(e)
            TelegramBot.send_raw_message('Error: {}'.format(e))
            break
        except KeyboardInterrupt:
            break

    print.info('Terminating')
    TelegramBot.send_raw_message('Terminating...')
    os.kill(os.getpid(), signal.SIGINT)