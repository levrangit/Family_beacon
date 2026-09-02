# Запуск тестовой среды Family Beacon

Эти инструкции используются по условному сигналу:

**«начнем запуск тестовой среды»**

## 1. Запуск backend

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

## 2. Проверка backend по сети

Во втором терминале:

```bash
curl -i http://127.0.0.1:8000/health
```

Ожидается HTTP 200 и ответ со статусом `ok`.

## 3. Проверка связи backend → удалённый Supabase

Во втором терминале:

```bash
curl -i http://127.0.0.1:8000/supabase-check
```

Команда проверяет доступ backend к удалённому Supabase.

## 4. Активация тестовой Supabase-сессии

В третьем терминале:

```bash
cd /workspaces/Family_beacon/backend && ./dev-auth
```

Ожидается:

```text
Supabase authentication: OK
User ID: ...
Fresh session: obtained
ACCESS_TOKEN_JWT: updated
```

JWT не выводить в чат и не передавать вручную.

## 5. Проверка авторизованного backend-запроса

После успешного `dev-auth`:

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

- `ACCESS_TOKEN_JWT` не публиковать в чате.
- Содержимое `backend/.env` не публиковать целиком.
- Тестовые credentials из `backend/.env` считаются временными и должны быть удалены после завершения соответствующих работ.
- Миграции Supabase создавать и изменять только локально, затем синхронизировать штатным способом.
- Ничего не менять в проекте Family Beacon без прямого разрешения пользователя.

## Быстрый порядок запуска

1. Запустить `uvicorn` на `0.0.0.0:8000`.
2. Проверить `/health`.
3. Проверить `/supabase-check`.
4. Выполнить `./dev-auth`.
5. Проверить `/me` с актуальным `ACCESS_TOKEN_JWT`.
6. Только после этого запускать integration/security tests.
