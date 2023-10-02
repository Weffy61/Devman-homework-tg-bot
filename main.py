import time
import requests
from environs import Env
import telegram


def send_notification(api_key, tg_token, chat_id):
    timestamp = ''
    headers = {
        'Authorization': f'Token {api_key}'
    }

    url_long_pooling = 'https://dvmn.org/api/long_polling/'
    bot = telegram.Bot(token=tg_token)
    while True:
        try:
            payload = {
                'timestamp': timestamp
            }
            response = requests.get(url_long_pooling, headers=headers, params=payload, timeout=100)
            response.raise_for_status()
            response_content = response.json()
            if response_content["status"] == "timeout":
                timestamp = response_content["timestamp_to_request"]
            elif response_content["status"] == "found":
                message = prepare_message(response_content)
                bot.send_message(chat_id=chat_id, text=message)
                timestamp = response_content["last_attempt_timestamp"]

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


def main():
    env = Env()
    env.read_env()
    devman_key = env.str('DEVMAN_API_KEY')
    telegram_token = env.str('TELEGRAM_TOKEN')
    chat_id = env.int('TELEGRAM_CHAT_ID')
    send_notification(devman_key, telegram_token, chat_id)


if __name__ == '__main__':
    main()
