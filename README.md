# DevMan HomeWork Telegram Bot

Телеграм-бот для получения результатов проверки ваших работ.

## Установка

```commandline
git clone https://github.com/Weffy61/Devman-homework-tg-bot.git
```

## Установка зависимостей
Переход в директорию с исполняемым файлом

```commandline
cd Devman-homework-tg-bot
```

Установка
```commandline
pip install -r requirements.txt
```

## Создание и настройка .env

Создайте в корне папки `Devman-homework-tg-bot` файл `.env`. Откройте его для редактирования любым текстовым редактором
и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.
Доступны следующие переменные:
 - DEVMAN_API_KEY - ваш devman API ключ 
 - TELEGRAM_TOKEN - ваш телеграм бот API ключ
 - TELEGRAM_CHAT_ID - ваш telegram id. Для получаения отпишите в [бота](https://telegram.me/userinfobot).
 
## Запуск

```commandline
python main.py
```

Как только ваша работа будет проверена, вы получите уведомление в telegram с положительным или отрицательным
результатом проверки, наименованием урока, а также ссылкой на него.  

## Цели проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков dvmn.org.

