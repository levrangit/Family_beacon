# Family Beacon — архитектура Telegram-бота

**Версия Telegram Bot:** `0.1.1`  
**Ветка:** `develop`  
**Назначение:** пользовательский Telegram-интерфейс Family Beacon для родителей и детей.

---

## 1. Назначение Telegram-бота

Telegram-бот Family Beacon является пользовательским интерфейсом системы.

Бот отвечает за:

- взаимодействие с пользователем в Telegram;
- определение пользователя по Telegram ID;
- отображение меню;
- обработку callback-кнопок;
- управление состоянием интерактивных диалогов;
- сбор пользовательского ввода;
- передачу команд и данных в Backend API;
- обработку голосовых сообщений через локальный Whisper.

Бот **не является источником бизнес-состояния**.

Основные бизнес-данные хранятся в Supabase и изменяются через Backend API.

Основной принцип:

```text
Telegram
   ↓
Telethon
   ↓
Telegram Bot
   ↓
Backend API
   ↓
Supabase
```

---

## 2. Технологический стек

Telegram-бот использует:

```text
Python
Telethon
tgnet
httpx
python-dotenv
OpenAI Whisper
PyTorch
```

Whisper использует модель `turbo`.

---

## 3. Telegram transport

Бот работает через **Telethon и MTProto**.

При отсутствии MTProto proxy используется `tgnet.TgNetConnection`.

При наличии FakeTLS MTProto proxy используется специальный адаптер `_FakeTlsProxyConnection`, который адаптирует формат proxy Telethon к FakeTLS API `tgnet`.

Итоговая схема:

```text
Telegram
    │
    ▼
Telethon
    │
    ├── direct MTProto
    │
    └── FakeTLS MTProto
            │
            ▼
          tgnet
```

---

## 4. Основной модуль `bot.py`

`telegram_bot/bot.py` является точкой запуска Telegram-клиента.

Он создаёт `TelegramClient` и `BackendClient` и регистрирует обработчики:

```text
/start
NewMessage
CallbackQuery
Voice messages
```

Основные обработчики:

```text
start_handler
registration_message_handler
callback_handler
voice_message_handler
```

---

## 5. Конфигурация

Конфигурация находится в `telegram_bot/config.py`.

Основные параметры:

```text
TELEGRAM_API_ID
TELEGRAM_API_HASH
TELEGRAM_BOT_TOKEN
TELEGRAM_BOT_SHARED_SECRET
FAMILY_BEACON_BACKEND_URL
TELEGRAM_SESSION_PATH
AUTHOR_TELEGRAM_ID
TELEGRAM_MTPROTO_PROXY_HOST
TELEGRAM_MTPROTO_PROXY_PORT
TELEGRAM_MTPROTO_PROXY_SECRET
```

Секреты не должны находиться в исходном коде или документации.

---

## 6. Определение пользователя

При `/start` бот получает Telegram ID отправителя и передаёт его Backend API:

```text
GET /telegram/lookup/{telegram_id}
```

с заголовком `X-Telegram-Bot-Key`.

Backend определяет тип пользователя:

```text
Telegram ID
     │
     ▼
Backend
     │
     ├── profiles.telegram_id → Parent / Admin
     │
     └── children.telegram_id → Child
```

Неизвестный пользователь получает выбор роли:

```text
Welcome
   ↓
Родитель / Ребёнок
```

---

## 7. Parent Menu

Основное родительское меню содержит:

```text
🌟 Семейный маяк · 0.1.1

🏠 Семья
👶 Дети
📨 Приглашения
ℹ️ О программе
```

Версия берётся из `telegram_bot/version.py`.

---

## 8. Раздел «Семья»

Раздел семьи является центральным рабочим экраном родителя.

Схема:

```text
🏠 Семья
├── название семьи
├── дети
├── Выдать приглашение
├── Профиль
└── Назад
```

Кнопка `👤 Профиль` находится непосредственно внутри меню `🏠 Семья`.

Для выбранного ребёнка доступны:

```text
👤 Профиль
⏱ Время
💻 Устройства
```

---

## 9. Переименование семьи

Поток:

```text
🏠 Семья
   ↓
название семьи
   ↓
ввод нового названия
   ↓
Backend
   ↓
Supabase
```

Бот использует in-memory состояние `family_rename_sessions`.

После успешного изменения пользователю показывается новое название семьи.

---

## 10. Регистрация родителя

Поток:

```text
/start
  ↓
Родитель
  ↓
ввод e-mail/логина
  ↓
ввод пароля
  ↓
POST /auth/register-parent
  ↓
Supabase Auth
  ↓
profiles
  ↓
Parent Menu
```

Регистрация использует `RegistrationSession`.

Основные состояния:

```text
waiting_login
      ↓
waiting_password
      ↓
completed
```

Пароль не хранится в Telegram state после завершения шага и передаётся Backend для регистрации.

---

## 11. Регистрация ребёнка

Поток регистрации ребёнка использует приглашение родителя:

```text
/start
   ↓
Ребёнок
   ↓
Invite Code
   ↓
Имя ребёнка
   ↓
Backend
   ↓
Supabase
   ↓
children
```

`RegistrationSession` использует состояния:

```text
waiting_invite_code
      ↓
waiting_child_name
      ↓
completed
```

Telegram ID ребёнка хранится в `children.telegram_id`.

---

## 12. Регистрация устройства ребёнка

Регистрация устройства является отдельным stateful workflow:

```text
Ребёнок
   ↓
💻 Устройства
   ↓
Регистрация устройства
   ↓
временный код
   ↓
Backend
   ↓
ожидание подтверждения родителя
```

Для него используется состояние `waiting_device_registration_code`.

После отправки кода возможны состояния, отражающие результат регистрации: ожидание подтверждения, одобрение, отклонение, истечение срока, неверный или уже использованный код.

---

## 13. Семейные приглашения

Родитель может открыть:

```text
📨 Приглашения
```

и:

- посмотреть существующие приглашения;
- создать новое приглашение.

Приглашение содержит:

```text
code
expires_at
status
```

Жизненный цикл:

```text
active
   ↓
used / expired / revoked
```

Постоянное состояние приглашений хранится в Supabase.

---

## 14. Просмотр детей

Родитель может открыть список детей и выбрать конкретного ребёнка.

Для ребёнка доступны:

```text
👤 Профиль
⏱ Время
💻 Устройства
```

Backend дополнительно проверяет принадлежность ребёнка семье текущего родителя.

---

## 15. Child Menu

После идентификации ребёнка бот показывает меню:

```text
🌟 Семейный маяк · 0.1.1

Привет, <имя>!

👤 Профиль
⏱ Время
💻 Устройства
```

Данные ребёнка загружаются через Telegram child backend API.

---

## 16. BackendClient

`telegram_bot/backend_client.py` является HTTP-клиентом Telegram-бота для Backend API.

Он обеспечивает транспорт:

```text
Telegram Bot
      ↓
HTTP
      ↓
FastAPI
```

Используется общий секрет:

```text
X-Telegram-Bot-Key
```

Группы операций:

```text
Identity
Parent registration
Parent profile
Family
Family rename
Children
Invites
Device registration
Agent installation
Account deletion
Child dashboard
```

Telegram-бот не должен напрямую обращаться к Supabase.

---

## 17. Аутентификация Telegram → Backend

Telegram API endpoints используют:

```text
X-Telegram-Bot-Key
```

Backend проверяет секрет и затем выполняет проверку Telegram ID и бизнес-прав.

Схема:

```text
Telegram Bot
    │
    │ X-Telegram-Bot-Key
    ▼
FastAPI
    │
    ├── authentication
    ├── Telegram ID
    └── business validation
          │
          ▼
      Supabase
```

---

## 18. Голосовой ввод

Начиная с версии **Telegram Bot 0.1.1**, бот поддерживает локальное распознавание Telegram voice messages.

Голосовой режим является опциональным и включается параметром:

```text
--whisper
```

Без параметра Whisper не загружается.

С параметром:

```text
Telegram voice
      ↓
Telethon
      ↓
OGG download
      ↓
Whisper turbo
      ↓
recognized text
      ↓
existing text handlers
```

---

## 19. Архитектура Whisper

Whisper загружается только при запуске с `--whisper`.

Модель:

```text
turbo
```

Модель кэшируется локально и загружается один раз на процесс.

Распознавание выполняется через отдельный worker thread, чтобы не блокировать основной async event loop.

---

## 20. Голос как альтернативный текстовый ввод

Ключевой принцип:

**Whisper не содержит отдельной бизнес-логики Telegram.**

После распознавания:

```text
voice message
     ↓
Whisper
     ↓
text
     ↓
_TextEventAdapter
     ↓
existing text handlers
```

Поэтому голос автоматически может использовать существующие сценарии, если соответствующий сценарий находится в ожидающем состоянии.

Фактически проверен сценарий:

```text
Семья
   ↓
Переименование семьи
   ↓
голосовое сообщение
   ↓
Whisper
   ↓
текст
   ↓
family rename handler
   ↓
Backend
   ↓
новое имя семьи
```

Это подтверждает полноценную интеграцию voice → text → existing workflow.

---

## 21. Ограничение голосового ввода

Голосовое сообщение не является самостоятельной универсальной командой.

Если пользователь отправляет произвольный голосовой текст без активного stateful-сценария, бизнес-обработчик может не выполнить никакого действия.

Схема:

```text
Whisper
   ↓
text
   ↓
stateful handlers
   ↓
нет активного состояния
   ↓
нет действия
```

Это нормальное поведение текущей архитектуры.

---

## 22. Callback architecture

Callback data разделена по доменам:

```text
role:*
parent:*
child:*
device_registration:*
agent_installation:*
```

Центральный callback handler маршрутизирует события соответствующим обработчикам.

---

## 23. Установка Family Beacon Agent

В Telegram-слое существует отдельный обработчик `agent_installation_handlers.py`.

Он создаёт installation request через Backend и получает installation code.

Архитектурно:

```text
Parent
   ↓
Telegram Bot
   ↓
Backend
   ↓
Installation Code
   ↓
Family Beacon Agent
```

В текущем коде обработчик установки существует отдельно от основного family menu. Кнопка установки Agent не является частью основного `_parent_family_buttons()`; существует отдельный builder с поддержкой установки. Это текущее состояние реализации.

---

## 24. Удаление аккаунта

Родительский профиль содержит:

```text
🗑 Забыть меня
```

Поток:

```text
Profile
   ↓
confirmation
   ↓
Backend
   ↓
delete_parent_account RPC
   ↓
Supabase
```

Операция требует явного подтверждения пользователя.

---

## 25. Архитектура состояния

Текущие Telegram-состояния хранятся в памяти процесса:

```text
registration_sessions
family_rename_sessions
```

При перезапуске процесса эти состояния теряются.

При этом бизнес-состояние хранится в Supabase:

```text
profiles
families
family_members
children
devices
invites
commands
time policies
usage
```

Принципиальное разделение:

```text
Telegram session state
        ≠
Business state
```

---

## 26. Разделение ответственности

### Telegram Bot

Отвечает за:

- UI;
- Telegram events;
- callback routing;
- Telegram ID;
- stateful user interaction;
- Whisper transcription;
- HTTP-запросы к Backend.

### Backend

Отвечает за:

- бизнес-логику;
- авторизацию Telegram-запросов;
- проверку прав;
- регистрацию;
- семьи;
- детей;
- приглашения;
- регистрацию устройств;
- Agent installation;
- удаление аккаунта.

### Supabase

Отвечает за:

- постоянное бизнес-состояние;
- PostgreSQL;
- Auth;
- RLS;
- RPC;
- целостность данных.

### Device Agent

Отвечает за:

- работу на компьютере ребёнка;
- регистрацию устройства;
- heartbeat;
- получение команд;
- выполнение команд;
- IPC и локальный UI.

---

## 27. Итоговая архитектура

```text
                         TELEGRAM
                            │
                            ▼
                    ┌───────────────┐
                    │   Telethon    │
                    │    MTProto    │
                    └───────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          Text / Callback          Voice
                 │                     │
                 │                 Whisper
                 │                     │
                 │                     ▼
                 │                   Text
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    Telegram Handlers
                            │
                            ▼
                    BackendClient
                            │
                  HTTP + Bot Secret
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    │ Telegram API  │
                    └───────┬───────┘
                            │
                            ▼
                  Telegram Services
                     │            │
                     ▼            ▼
             Parent Service   Child Service
                     │            │
                     └──────┬─────┘
                            ▼
                       Supabase
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
       profiles          families          children
                                              │
                                              ▼
                                           devices
```

Отдельный контур Agent:

```text
Parent
  │
  ▼
Telegram Bot
  │
  ▼
Backend
  │
  ▼
Installation Code
  │
  ▼
Device Agent
  │
  ▼
Device
```

---

## 28. Версия 0.1.1

Версия `0.1.1` фиксирует состояние Telegram-бота после интеграции голосового ввода.

В неё входят:

- Telethon/MTProto transport;
- FakeTLS proxy support через `tgnet`;
- родительский интерфейс;
- семейный интерфейс;
- профиль внутри меню семьи;
- приглашения;
- просмотр детей;
- регистрационные state machines;
- регистрация устройств;
- Agent installation API integration;
- локальный Whisper;
- опциональный запуск через `--whisper`;
- передача Whisper-текста в существующие handlers;
- диагностическое логирование голосовых сообщений.

Ключевой результат версии:

```text
Voice
  ↓
Whisper
  ↓
Text
  ↓
Existing Telegram workflow
```

без создания отдельной бизнес-логики для голосовых команд.

---

## 29. Тестирование

Telegram-тесты находятся отдельно:

```text
telegram_bot/tests_telegram_bot/
```

Покрываются, в частности:

```text
test_about.py
test_agent_installation.py
test_backend_client.py
test_device_registration.py
test_family_rename_handlers.py
test_parent_family_menu.py
test_parent_menu.py
test_registration.py
test_version.py
test_voice_handler.py
```

Особенно важен `test_voice_handler.py`, проверяющий передачу распознанного текста в существующий message flow.

Telegram-тесты не должны автоматически переноситься в структуру backend-тестов.

---

## 30. Главный архитектурный принцип

```text
Telegram
    = интерфейс и пользовательское взаимодействие

Backend
    = бизнес-логика и контроль доступа

Supabase
    = источник постоянного бизнес-состояния

Whisper
    = преобразование голос → текст

Device Agent
    = исполнитель действий на устройстве ребёнка
```

Главный принцип:

**Telegram-бот не должен дублировать бизнес-логику Backend. Голосовой ввод также не должен создавать отдельную бизнес-логику: он преобразует голос в текст и передаёт его существующему пользовательскому workflow.**
