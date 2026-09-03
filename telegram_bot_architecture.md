# Family Beacon — концепция Telegram-бота и регистрации пользователей

## 1. Общая концепция

Telegram-бот Family Beacon является пользовательским интерфейсом системы для родителей и детей.

Для работы с Telegram используется **Telethon на базе MTProto**, а не Telegram Bot API.

Основная задача бота — определить пользователя по Telegram ID и предоставить соответствующий интерфейс.

Общий сценарий:

```text
/start
   ↓
Telegram ID
   ↓
проверка profiles
   ├── найден → Parent Menu
   │
   └── не найден
          ↓
       проверка children
          ├── найден → Child Menu
          │
          └── не найден
                 ↓
        Welcome / выбор роли
```

Начальный экран:

```text
👋 Добро пожаловать в Family Beacon!
Выберите свою роль, чтобы продолжить:

[ 👨 Родитель ]
[ 👦 Ребёнок ]
```

---

## 2. Регистрация родителя

Пользователь выбирает:

```text
[ 👨 Родитель ]
```

После этого бот последовательно запрашивает:

```text
Email
↓
Password
```

После получения данных Telegram-бот вызывает Backend API:

```text
POST /auth/register-parent
```

Передаваемые данные:

```text
telegram_id
login
password
```

Backend регистрирует пользователя через Supabase Auth.

Telegram ID передаётся в metadata создаваемого пользователя.

После создания пользователя механизм Supabase автоматически создаёт соответствующую запись в:

```text
profiles
```

с сохранением:

```text
profiles.telegram_id
```

После успешной регистрации пользователь попадает в:

```text
Parent Menu
```

### Важное правило

Регистрация родителя **не создаёт автоматически новую family**.

Создание семьи является отдельной операцией и выполняется в соответствующем пользовательском сценарии.

---

## 3. Идентификация зарегистрированного пользователя

При каждом обращении пользователя к боту используется его Telegram ID.

Проверка выполняется в следующем порядке:

```text
Telegram ID
   ↓
profiles.telegram_id
   ↓
если найден
   ↓
Parent Menu
```

Если пользователь не найден среди родителей:

```text
Telegram ID
   ↓
children.telegram_id
   ↓
если найден
   ↓
Child Menu
```

Если пользователь не найден ни в одной из систем:

```text
Telegram ID
   ↓
Welcome
   ↓
выбор роли
```

---

## 4. Регистрация ребёнка

Пользователь выбирает:

```text
[ 👦 Ребёнок ]
```

Бот запрашивает:

```text
Имя
↓
Invite Code
```

После получения данных выполняется проверка приглашения.

Если invite code корректен:

```text
Telegram ID
      ↓
Invite Code
      ↓
определение family
      ↓
создание / привязка child
      ↓
сохранение Telegram ID
      ↓
Child Menu
```

Результатом регистрации является запись ребёнка, связанная с соответствующей family и Telegram ID.

Invite code является частью процесса регистрации и **не является постоянным пунктом меню ребёнка**.

---

## 5. Логика определения роли

Telegram ID является основным идентификатором пользователя в Telegram-интерфейсе.

Целевая логика:

```text
Telegram ID
    │
    ├── profiles.telegram_id
    │       └── Parent
    │
    └── children.telegram_id
            └── Child
```

Приоритет проверки:

```text
profiles
   ↓
children
```

После определения зарегистрированного пользователя бот сразу открывает соответствующее меню.

---

## 6. Parent Menu

После регистрации/идентификации родитель получает Parent Menu.

Меню является основным интерфейсом родителя для управления Family Beacon.

Конкретный набор функций меню развивается отдельно, но архитектурно родитель работает через Telegram-бота с Backend API, а Backend взаимодействует с Supabase.

```text
Parent
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

## 7. Child Menu

После регистрации/идентификации ребёнок получает Child Menu.

Ребёнок не проходит повторную регистрацию при каждом запуске бота.

Система определяет его по:

```text
children.telegram_id
```

и сразу открывает соответствующий интерфейс.

```text
Child
   ↓
Telegram ID
   ↓
children
   ↓
Child Menu
```

---

## 8. Backend

Telegram-бот не должен самостоятельно реализовывать бизнес-логику работы с Supabase.

Архитектурно:

```text
Telethon Bot
      ↓
Backend API
      ↓
Supabase
```

Telegram-бот отвечает преимущественно за:

- взаимодействие с пользователем;
- состояние Telegram-сессии;
- получение Telegram ID;
- отображение меню;
- сбор регистрационных данных;
- вызов Backend API.

Backend отвечает за:

- регистрацию;
- авторизацию;
- бизнес-правила;
- работу с Family;
- работу с children;
- проверку invite code;
- взаимодействие с Supabase;
- контроль доступа.

Supabase является хранилищем бизнес-состояния системы.

---

## 9. Update Service

Telegram-бот должен обновляться без ручного `git pull` на production-сервере.

Целевая архитектура:

```text
GitHub
   ↓
GitHub Actions
   ├── tests
   ├── security checks
   ├── SonarCloud
   └── build release
           ↓
      Release Artifact
           ↓
      Update Service
           ├── download
           ├── verify
           ├── install
           ├── health check
           ├── activate
           └── rollback
                  ↓
             Telethon Bot
```

Production не должен зависеть от состояния Git working tree.

Каждый релиз является отдельной версией.

Например:

```text
/opt/family-beacon/
├── releases/
│   ├── 1.0.0/
│   ├── 1.1.0/
│   └── 1.2.0/
│
├── current -> releases/1.2.0
│
└── shared/
    ├── .env
    └── telegram.session
```

Секреты и Telegram session не должны находиться внутри release directory.

Перед активацией новой версии Update Service должен:

1. скачать release artifact;
2. проверить его целостность;
3. установить новую версию;
4. выполнить health check;
5. активировать новую версию;
6. сохранить предыдущую версию;
7. выполнить rollback при неудачном запуске или health check.

---

## 10. Production services

На первом этапе production предполагается организовать через systemd.

Основные сервисы:

```text
family-beacon-telegram.service
family-beacon-backend.service
family-beacon-updater.service
```

Telegram-бот должен корректно обрабатывать SIGTERM и выполнять graceful shutdown.

Это позволяет Update Service безопасно заменить текущую версию без повреждения Telegram session и бизнес-состояния.

---

## 11. Работа с базой данных

Бизнес-состояние хранится в Supabase.

Telegram-бот не является источником истины для:

- пользователей;
- family;
- children;
- устройств;
- команд;
- политик;
- истории действий.

Telegram session является техническим состоянием Telegram-клиента и хранится отдельно от release.

Изменения схемы Supabase должны выполняться через миграции.

Для несовместимых изменений используется последовательность:

```text
Expand
   ↓
Migrate
   ↓
Contract
```

Это позволяет обновлять Backend и Telegram-бот без резкого нарушения совместимости.

---

## 12. Принцип разделения ответственности

Итоговая архитектура:

```text
                   Telegram
                      │
                      ▼
                 Telethon
                      │
                      ▼
              Telegram Bot
                      │
                      ▼
                 Backend API
                      │
                      ▼
                  Supabase
                 /        \
                /          \
           profiles       children
                │            │
             Parent         Child
```

Отдельный контур обновления:

```text
GitHub
   ↓
GitHub Actions
   ↓
Release
   ↓
Update Service
   ↓
Telethon Bot
```

Главный принцип:

**Telegram — интерфейс, Backend — бизнес-логика, Supabase — источник бизнес-состояния, Update Service — управление жизненным циклом production-релизов.**
