# Device Agent 0.1.0 — карта MVP

## Цель

Создать минимально работающий Windows Device Agent v0.1.0, который запускается, безопасно определяет своё окружение и формирует данные для будущей связи с Backend.

На этом этапе Agent не регистрирует устройство, не выполняет pairing и не хранит секреты.

## 1. Аудит существующего Agent

Перед изменениями:

- изучить текущую структуру `agent/`;
- проверить существующие `api.py`, `auth.py`, `config.py`, `worker.py`, `executor.py` и тесты;
- определить, что уже работает и может быть переиспользовано;
- перед созданием тестов прочитать `backend/tests/test_rules.md`;
- не переписывать существующий код без необходимости.

## 2. Windows Machine GUID

Agent получает:

```text
windows_machine_guid
```

Источник:

```text
HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid
```

Для MVP это временный основной идентификатор установки Windows.

Позже будет добавлен `hardware_fingerprint`.

## 3. Hostname

Agent получает hostname только как отображаемую информацию для пользователя и родителя.

Пример:

```text
Компьютер: IVAN-PC
Платформа: Windows
```

Hostname не участвует в технической идентичности устройства.

## 4. Windows-пользователь

Agent получает:

- Windows SID — основной идентификатор OS-пользователя;
- username — дополнительная отображаемая информация.

Это создаёт основу для будущей модели:

```text
computer + Windows SID -> Family Beacon child
```

## 5. Windows-сессия

Agent определяет:

```text
os_session_identity
```

На MVP сначала необходимо надёжно определить текущую сессию. Полное отслеживание переключений пользователей будет следующим этапом.

## 6. Версионирование

Agent является самостоятельным компонентом и имеет собственную версию:

```text
Device Agent v0.1.0
```

Agent сообщает:

```text
component = device-agent
version = 0.1.0
```

Версионирование соответствует `docs/VERSIONING.md`.

## 7. Identity Payload

Agent должен уметь сформировать:

```text
component
agent_version
platform
windows_machine_guid
hostname
os_user_sid
os_username
os_session_identity
```

Пример:

```json
{
  "component": "device-agent",
  "version": "0.1.0",
  "platform": "windows",
  "windows_machine_guid": "...",
  "hostname": "IVAN-PC",
  "os_user_sid": "S-1-5-21-...",
  "os_username": "Ivan",
  "os_session_identity": "..."
}
```

## 8. Локальное состояние и безопасность

На этом этапе не создаём полноценное локальное хранилище серверного состояния.

Не храним:

- device credentials;
- access tokens;
- refresh tokens;
- private keys;
- child binding;
- pairing state.

Отдельным этапом будет спроектирована модель:

```text
local state
protected local storage
remote Backend state
```

Backend должен стать источником истины для регистрации, привязок и политик.

## 9. Backend

Существующий Backend API изучаем для понимания текущей device architecture.

Пока не добавляем:

- новые migrations;
- новые pairing endpoints;
- регистрацию устройства;
- child binding.

## 10. Тесты

Перед созданием тестов обязательно прочитать:

```text
backend/tests/test_rules.md
```

Проверить:

- получение MachineGuid;
- получение hostname;
- получение Windows SID;
- получение username;
- определение session identity;
- формирование identity payload;
- получение версии Agent;
- обработку ошибок Windows Registry/API.

## Что НЕ входит в Device Agent v0.1.0

- pairing code;
- Telegram integration;
- parent approval;
- device registration;
- device_id;
- device credentials;
- child binding;
- hardware fingerprint;
- полноценная policy system;
- сложная update system.

## Ближайшая последовательность

```text
1. Аудит существующего Agent
2. Изучение VERSIONING.md и test_rules.md
3. Windows environment/identity
4. Agent version
5. Identity Payload
6. Тесты
7. Проверка реального запуска Agent
```

## Следующие этапы

После работающего MVP:

```text
Модель безопасности и состояния
        ↓
Pairing code
        ↓
Child Telegram
        ↓
Parent approval
        ↓
Backend registration
        ↓
Secure credentials
        ↓
device + OS user -> child
        ↓
policies
```
