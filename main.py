import time
import requests
from environs import Env
import telegram


def devman_api(api_key, tg_token, chat_id):
    timestamp = ''
    headers = {
        'Authorization': f'Token {api_key}'
    }

    url_long_pooling = 'https://dvmn.org/api/long_polling/'

    while True:
        try:
            payload = {
                'timestamp': timestamp
            }
            response = requests.get(url_long_pooling, headers=headers, params=payload, timeout=100)
            response.raise_for_status()
            if response.json()["status"] == "timeout":
                timestamp = response.json()["timestamp_to_request"]
            elif response.json()["status"] == "found":
                message = prepare_message(response.json())
                send_tg_message(tg_token, message, chat_id)
                timestamp = response.json()["last_attempt_timestamp"]

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
    message = f'У вас проверили работу "{lesson_title}"\nСсылка на урок "{lesson_url}"' \
              f'\n{result_of_checking}'
    return message


def send_tg_message(tg_token, message, chat_id):
    bot = telegram.Bot(token=tg_token)
    bot.send_message(chat_id=chat_id, text=message)


def main():
    env = Env()
    env.read_env()
    devman_key = env.str('DEVMAN_API_KEY')
    telegram_token = env.str('TELEGRAM_TOKEN')
    chat_id = env.int('CHAT_ID')
    devman_api(devman_key, telegram_token, chat_id)


if __name__ == '__main__':
    main()


