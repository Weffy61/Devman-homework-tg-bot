import logging
import textwrap
import time

import requests
from environs import Env
import telegram
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


logger = logging.getLogger('Telegram logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_notification(api_key, tg_token, chat_id):

    timestamp = ''
    headers = {
        'Authorization': f'Token {api_key}'
    }

    url_long_pooling = 'https://dvmn.org/api/long_polling/'
    bot = telegram.Bot(token=tg_token)
    logger.info('Бот запущен')
    while True:
        try:
            payload = {
                'timestamp': timestamp
            }
            response = requests.get(
                url_long_pooling,
                headers=headers,
                params=payload,
                timeout=100
            )
            response.raise_for_status()
            check_status = response.json()
            if check_status["status"] == "timeout":
                timestamp = check_status["timestamp_to_request"]
            elif check_status["status"] == "found":
                message = prepare_message(check_status)
                bot.send_message(
                    chat_id=chat_id,
                    text=message
                )
                timestamp = check_status["last_attempt_timestamp"]

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue
        except Exception as e:
            logger.error(f'Бот завершил работу с ошибкой: {e}', exc_info=True)
            logger.info('Бот будет перезапущен через 10 секунд')
            time.sleep(10)
            continue


def prepare_message(response):
    lesson_title = response['new_attempts'][0]['lesson_title']
    lesson_url = response['new_attempts'][0]['lesson_url']
    result_of_checking = 'Преподавателю всё понравилось, можно приступать ' \
                         'к следущему уроку!'
    if response['new_attempts'][0]['is_negative']:
        result_of_checking = 'К сожалению, в работе нашлись ошибки.'
    message = textwrap.dedent(f'''
    У вас проверили работу "{lesson_title}" 
    Ссылка на урок "{lesson_url}"
    {result_of_checking}
    ''')
    return message


def main():
    env = Env()
    env.read_env()
    devman_key = env.str('DEVMAN_API_KEY')
    group_id = env.int('TELEGRAM_GROUP_ID')
    chat_id = env.int('TELEGRAM_CHAT_ID')
    telegram_check_token = env.str('TELEGRAM_CHECK_TOKEN')
    telegram_logs_token = env.str('TELEGRAM_LOGS_TOKEN')

    tg_bot_logs = telegram.Bot(token=telegram_logs_token)
    logger.setLevel(logging.INFO)
    telegram_logs_handler = TelegramLogsHandler(
        tg_bot=tg_bot_logs,
        chat_id=chat_id
    )
    logger.addHandler(telegram_logs_handler)

    send_notification(devman_key, telegram_check_token, group_id)


if __name__ == '__main__':
    main()
