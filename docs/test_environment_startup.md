# Запуск тестовой среды Family Beacon

Эти инструкции используются по условному сигналу:

**«начнем запуск тестовой среды»**

## 1. Авторизация Supabase CLI в удалённом Supabase

Перед работой с удалённым проектом авторизуй Supabase CLI:

```bash
cd /workspaces/Family_beacon && supabase login
```

CLI попросит Supabase Access Token. Сам токен не публиковать в чате и не записывать в файлы проекта.

После входа проверь, что CLI видит проекты:

```bash
cd /workspaces/Family_beacon && supabase projects list
```

Ожидается список доступных Supabase-проектов.

**Важно:** `SUPABASE_ACCESS_TOKEN` — это токен Supabase CLI. Он отличается от `ACCESS_TOKEN_JWT`, который используется как JWT пользователя Family Beacon для авторизованных запросов.

## 2. Запуск backend

Открой отдельный терминал Codespace:

```bash
cd /workspaces/Family_beacon/backend && \
PYTHONPATH=. ./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Оставь этот терминал работающим.

Ожидаемый результат:

```text
Uvicorn running on http://0.0.0.0:8000
```

## 3. Проверка backend по сети

Во втором терминале:

```bash
curl -i http://127.0.0.1:8000/health
```

Ожидается HTTP 200 и ответ со статусом `ok`.

## 4. Проверка связи backend → удалённый Supabase

Во втором терминале:

```bash
curl -i http://127.0.0.1:8000/supabase-check
```

Команда проверяет доступ backend к удалённому Supabase.

## 5. Актуализация пользовательского Supabase JWT

В проекте есть штатный скрипт:

`backend/refresh_access_token.py`

Он выполняет вход тестового пользователя в Supabase через `TEST_EMAIL` и `TEST_PASSWORD` из `backend/.env`, получает свежий `access_token` и обновляет локальную переменную:

```text
ACCESS_TOKEN_JWT=
```

Скрипт не выводит сам JWT в консоль.

При начале работы с тестовой средой **сначала используй этот скрипт, если `ACCESS_TOKEN_JWT` может быть устаревшим**:

```bash
cd /workspaces/Family_beacon/backend && \
python refresh_access_token.py
```

После обновления токена для текущей shell-сессии:

```bash
cd /workspaces/Family_beacon/backend && \
set -a && source .env && set +a
```

Также в проекте существует команда `./dev-auth`, которая предназначена для активации тестовой Supabase-сессии. Если она используется как основной сценарий запуска, она также должна обеспечивать получение актуального `ACCESS_TOKEN_JWT`.

JWT не выводить в чат и не передавать вручную.

## 6. Проверка авторизованного backend-запроса

После успешного обновления токена:

```bash
cd /workspaces/Family_beacon/backend && \
TOKEN=$(grep '^ACCESS_TOKEN_JWT=' .env | cut -d= -f2-) && \
curl -sS \
  -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/me
```

Этот запрос проверяет цепочку:

```text
curl
 ↓
FastAPI
 ↓
Authorization / JWT
 ↓
Supabase Auth
 ↓
profiles
 ↓
/me
```

## Правила безопасности

- Supabase CLI Access Token не публиковать в чате.
- `ACCESS_TOKEN_JWT` не публиковать в чате.
- Содержимое `backend/.env` не публиковать целиком.
- Тестовые credentials из `backend/.env` считаются временными и должны быть удалены после завершения соответствующих работ.
- Миграции Supabase создавать и изменять только локально, затем синхронизировать штатным способом.
- Ничего не менять в проекте Family Beacon без прямого разрешения пользователя.

## Быстрый порядок запуска

1. Выполнить `supabase login`.
2. Проверить `supabase projects list`.
3. Запустить `uvicorn` на `0.0.0.0:8000`.
4. Проверить `/health`.
5. Проверить `/supabase-check`.
6. Выполнить `python refresh_access_token.py` для получения актуального `ACCESS_TOKEN_JWT`.
7. Загрузить обновлённые переменные из `.env` в текущую shell-сессию.
8. Проверить `/me` с актуальным `ACCESS_TOKEN_JWT`.
9. Только после этого запускать integration/security tests.
