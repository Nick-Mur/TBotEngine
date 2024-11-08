# TBotEngine

## Оглавление

1. [Описание проекта](#описание-проекта)
2. [Особенности](#особенности)
3. [Установка](#установка)
4. [Структура проекта](#структура-проекта)
5. [Как с этим работать](#как-с-этим-работать)
    - [Расширение команд](#расширение-команд)
    - [Добавление фраз и медиа](#добавление-фраз-и-медиа)
    - [Добавление шрифтов](#добавление-шрифтов)
    - [Редактирование связей между сообщениями](#редактирование-связей-между-сообщениями)
    - [Редактирование констант](#редактирование-констант)
6. [Лицензия](#лицензия)

## Описание проекта

**TBotEngine** — это движок для создания Telegram-ботов с готовым набором базовых команд, встроенной монетизацией и уникальной системой "одного сообщения", где основной текст отображается в рамках одного редактируемого сообщения. Данный подход обеспечивает более удобное взаимодействие пользователя с ботом, минимизируя количество сообщений в чате.

## Особенности

- **Готовый набор базовых команд**: Начните разработку с уже настроенными основными командами, такими как `/start`, `/save`, `/ads`' и другие.
- **Встроенная монетизация**: Поддержка платежей через Telegram, управление токенами, рекламой и транзакциями.
- **Система одного сообщения**: Основной контент отображается в одном редактируемом сообщении, улучшая пользовательский опыт.
- **Гибкая структура**: Возможность легко расширять функциональность, добавлять новые команды, фразы, медиа и многое другое.

## Установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/Nick-Mur/TBotEngine.git
   ```

2. **Перейдите в директорию проекта:**

   ```bash
   cd TBotEngine
   ```

3. **Создайте виртуальное окружение и активируйте его:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Для Unix или MacOS
   venv\Scripts\activate     # Для Windows
   ```

4. **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Создайте файл `.env`** в корневой директории проекта и добавьте необходимые переменные окружения:

   ```env
   BOT_TOKEN=ваш_токен_бота
   WEBHOOK_HOST=ваш_хост_вебхука_если_используется
   ```

6. **Запустите бота:**

   ```bash
   python main.py
   ```

   - Если вы используете вебхук, убедитесь, что `WEBHOOK_HOST` настроен правильно и доступен по HTTPS.
   - Если вы используете polling, оставьте `WEBHOOK_HOST` пустым или установите в `None` в файле `.env`.

## Структура проекта

```
TBotEngine/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── bot.py
│   └── consts.py
├── main.py
├── database/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── db_session.py
│   │   └── db_consts.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── choices.py
│   │   ├── game.py
│   │   ├── promo.py
│   │   ├── transactions.py
│   │   └── user.py
│   ├── db_operations.py
│   └── project.db
├── find_message/
│   ├── __init__.py
│   └── find_message_0.py
├── handlers/
│   ├── __init__.py
│   ├── callbacks.py
│   ├── commands.py
│   └── messages.py
├── middlewares/
│   ├── __init__.py
│   ├── custom_middleware.py
│   └── special_func.py
├── resources/
│   ├── __init__.py
│   ├── buttons.py
│   ├── keyboards.py
│   ├── media/
│   │   ├── __init__.py
│   │   ├── images/
│   │   │   ├── photo_1.jpg
│   │   │   └── photo_2.jpg
│   │   ├── media_0.py
│   │   └── media_1.py
│   ├── messages/
│   │   ├── __init__.py
│   │   ├── messages_0.py
│   │   ├── messages_1.py
│   │   └── find_message_0.py
│   └── phrases/
│       ├── __init__.py
│       ├── phrases_0.py
│       ├── phrases_1.py
│       └── special_phrases.py
├── settings/
│   ├── __init__.py
│   └── config_reader.py
└── utils/
    ├── __init__.py
    ├── decorators.py
    ├── edit_func.py
    ├── message_utils.py
    ├── media_functions_0.py
    └── media_functions_1.py
```

### Разъяснение структуры

- **app/**: Инициализация бота и основные константы.
  - `bot.py`: Создание экземпляров бота и диспетчера.
  - `consts.py`: Глобальные константы проекта.

- **main.py**: Точка входа в приложение, запуск бота и настройка вебхука или polling.

- **database/**: Все, что связано с базой данных.
  - `core/`: Основные инструменты для работы с БД.
    - `db_session.py`: Создание сессий для работы с БД.
    - `db_consts.py`: Константы для работы с БД.
  - `models/`: Модели SQLAlchemy.
    - `user.py`, `game.py`, `promo.py` и др.: Определение таблиц базы данных.
  - `db_operations.py`: Функции для операций с БД.
  - `project.db`: Файл базы данных SQLite.

- **find_message/**: Логика связи между сообщениями.
  - `find_message_0.py`: Файл, в котором определяются связи между сообщениями.

- **handlers/**: Обработчики событий Telegram.
  - `commands.py`: Обработка команд, таких как `/start`, `/help`.
  - `callbacks.py`: Обработка callback-запросов от inline-кнопок.
  - `messages.py`: Обработка текстовых сообщений от пользователей.

- **middlewares/**: Промежуточные слои для обработки обновлений.
  - `custom_middleware.py`: Пользовательские middleware.
  - `special_func.py`: Специальные функции для обработки обновлений.

- **resources/**: Ресурсы проекта.
  - `buttons.py`: Определение inline-кнопок.
  - `keyboards.py`: Сборка клавиатур из кнопок.
  - `media/`: Медиафайлы и их описание.
    - `images/`: Папка с изображениями.
    - `media_0.py`, `media_1.py`: Модули с описанием медиафайлов.
  - `messages/`: Сообщения бота.
    - `messages_0.py`, `messages_1.py`: Определение сообщений.
    - `find_message_0.py`: Логика переходов между сообщениями.
  - `phrases/`: Текстовые фразы.
    - `phrases_0.py`, `phrases_1.py`, `special_phrases.py`: Фразы для различных ситуаций.

- **settings/**: Настройки проекта.
  - `config_reader.py`: Чтение переменных окружения из `.env`.

- **utils/**: Утилитарные функции и декораторы.
  - `decorators.py`: Декораторы для форматирования текста.
  - `edit_func.py`: Функции для редактирования сообщений.
  - `message_utils.py`: Утилиты для работы с сообщениями.
  - `media_functions_0.py`, `media_functions_1.py`: Функции для работы с медиа.

## Как с этим работать

### 1. Расширение команд

Вы можете добавлять новые команды, расширяя функциональность бота.

**Как добавить новую команду:**

1. **Создайте функцию-обработчик** в файле `handlers/commands.py` или создайте новый файл в `handlers/`.

   ```python
   # handlers/commands.py
   from aiogram import Router
   from aiogram.types import Message

   router = Router()

   @router.message(commands=['my_command'])
   async def my_command_handler(message: Message):
       await message.reply("Это моя новая команда!")
   ```

2. **Подключите новый роутер** в `main.py`:

   ```python
   # main.py
   from handlers import commands

   dp.include_router(commands.router)
   ```

### 2. Добавление фраз и медиа

Вы можете создавать свои собственные фразы и добавлять медиа, объединяя их в сообщения.

**Как добавить новые фразы:**

1. **Создайте новый файл** в `resources/phrases/`, например, `phrases_custom.py`.

   ```python
   # resources/phrases/phrases_custom.py
   phrases_dict = {
       'welcome': 'Добро пожаловать!',
       'farewell': 'До свидания!'
   }
   ```

2. **Импортируйте и используйте фразы** в вашем коде:

   ```python
   from resources.phrases.phrases_custom import phrases_dict

   await message.reply(phrases_dict['welcome'])
   ```

**Как добавить новые медиа:**

1. **Поместите файлы медиа** в папку `resources/media/images/`.

2. **Определите медиафайлы** в соответствующем модуле, например, `media_custom.py`:

   ```python
   # resources/media/media_custom.py
   media_files = {
       'welcome_image': 'welcome.jpg',
       'goodbye_image': 'goodbye.jpg'
   }
   ```

3. **Используйте медиафайлы** в сообщениях:

   ```python
   from resources.media.media_custom import media_files
   from aiogram.types import FSInputFile

   image = FSInputFile(f"resources/media/images/{media_files['welcome_image']}")
   await bot.send_photo(chat_id=message.chat.id, photo=image)
   ```

**Объединение фраз и медиа в сообщения:**

1. **Создайте новое сообщение** в `resources/messages/`, например, `messages_custom.py`:

   ```python
   # resources/messages/messages_custom.py
   message_welcome = {
       'text': 'welcome',
       'media': 'welcome_image',
       'keyboard': 'main_keyboard'
   }
   ```

2. **Обновите обработчик для отправки этого сообщения**:

   ```python
   from resources.messages.messages_custom import message_welcome
   from utils.message_utils import update_msg

   async def send_welcome_message(message: Message):
       msg = await update_msg(message_welcome, message)
       await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])
   ```

### 3. Добавление шрифтов

Вы можете добавлять свои собственные шрифты или стили для форматирования текста.

**Как добавить новый шрифт или стиль:**

1. **Добавьте функцию-декоратор** в `utils/decorators.py`:

   ```python
   # utils/decorators.py

   def italic(text):
       return f"<i>{text}</i>"
   ```

2. **Используйте декоратор** в вашем коде:

   ```python
   from utils.decorators import italic

   formatted_text = italic("Это курсивный текст")
   await message.reply(formatted_text, parse_mode='HTML')
   ```

### 4. Редактирование связей между сообщениями

Вы можете редактировать связи между сообщениями в файле `find_message/find_message_0.py`.

**Как редактировать связи:**

1. **Откройте файл** `find_message/find_message_0.py`.

2. **Добавьте или измените связи между сообщениями**:

   ```python
   # find_message/find_message_0.py

   message_flow = {
       'start': 'message_0',
       'message_0': {
           'next': 'message_1',
           'options': {
               'option_a': 'message_2a',
               'option_b': 'message_2b'
           }
       },
       'message_1': {
           'next': 'message_end'
       },
       # Добавьте свои сообщения и связи
   }
   ```

3. **Используйте эти связи** в обработчиках для навигации:

   ```python
   # handlers/messages.py

   from find_message.find_message_0 import message_flow

   async def navigate_messages(message: Message):
       current_state = 'start'
       next_message_key = message_flow[current_state]['next']
       # Логика для отправки следующего сообщения
   ```

### 5. Редактирование констант

Вы можете изменять константы в файле `app/consts.py` для настройки приложения.

**Доступные константы и их описание:**

- `DEBUG`: Режим отладки (True/False). При `True` выводится дополнительная информация об ошибках.
- `DB_PATH`: Путь к файлу базы данных SQLite.
- `MEDIA_PHOTO`: Путь к директории с изображениями.
- `CHANNEL_IDS`: Список каналов, на которые должен быть подписан пользователь.
- `ADMINS`: Список Telegram ID администраторов бота.
- `OWNER`: Telegram ID владельца бота.

**Как редактировать константы:**

1. **Откройте файл** `app/consts.py`.

2. **Измените значения констант** по своему усмотрению:

   ```python
   # app/consts.py

   DEBUG = False
   DB_PATH = 'database/my_custom_db.db'
   MEDIA_PHOTO = 'resources/media/images/'
   CHANNEL_IDS = ['@my_channel']
   ADMINS = [123456789]
   OWNER = 123456789
   ```

   - **Пример использования констант**:

     ```python
     # Использование константы CHANNEL_IDS для проверки подписки
     from app.consts import CHANNEL_IDS

     async def check_user_subscription(user_id):
         for channel in CHANNEL_IDS:
             # Логика проверки подписки пользователя на канал
     ```
