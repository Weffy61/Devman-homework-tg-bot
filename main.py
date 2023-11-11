import time
import requests
from environs import Env
import telegram
import textwrap
import logging


def send_notification(api_key, tg_token, chat_id):
    timestamp = ''
    headers = {
        'Authorization': f'Token {api_key}'
    }

    url_long_pooling = 'https://dvmn.org/api/long_polling/'
    bot = telegram.Bot(token=tg_token)
    logging.info('bot started')
    while True:
        try:
            payload = {
                'timestamp': timestamp
            }
            response = requests.get(url_long_pooling, headers=headers, params=payload, timeout=100)
            response.raise_for_status()
            check_status = response.json()
            if check_status["status"] == "timeout":
                timestamp = check_status["timestamp_to_request"]
            elif check_status["status"] == "found":
                message = prepare_message(check_status)
                bot.send_message(chat_id=chat_id, text=message)
                timestamp = check_status["last_attempt_timestamp"]

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue


def prepare_message(response):
    lesson_title = response['new_attempts'][0]['lesson_title']
    lesson_url = response['new_attempts'][0]['lesson_url']
    result_of_checking = 'Преподавателю всё понравилось, можно приступать к следущему уроку!'
    if response['new_attempts'][0]['is_negative']:
        result_of_checking = 'К сожалению, в работе нашлись ошибки.'
    message = textwrap.dedent(f'''
    У вас проверили работу "{lesson_title}" 
    Ссылка на урок "{lesson_url}"
    {result_of_checking}
    ''')
    return message


def main():
    logging.basicConfig(level=logging.DEBUG)
    env = Env()
    env.read_env()
    devman_key = env.str('DEVMAN_API_KEY')
    telegram_token = env.str('TELEGRAM_TOKEN')
    chat_id = env.int('TELEGRAM_CHAT_ID')
    send_notification(devman_key, telegram_token, chat_id)


if __name__ == '__main__':
    main()
