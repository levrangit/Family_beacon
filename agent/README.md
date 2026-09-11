# Family Beacon Device Agent 0.1.1

Device Agent для Family Beacon, работающий только в Windows.

## Назначение

Device Agent работает на компьютере ребёнка под управлением Windows и обеспечивает локальный контур взаимодействия между Windows, Family Beacon Backend и пользовательским Tray-интерфейсом.

Версия **0.1.1** формирует следующую рабочую основу:

- сбор идентификаторов Windows-устройства;
- локальная конфигурация Agent;
- генерация и локальное хранение постоянного секрета установки Agent;
- взаимодействие с Family Beacon Backend;
- создание запроса на регистрацию устройства;
- управление локальным состоянием регистрации;
- работа в качестве Windows Service;
- аутентифицированное локальное IPC-взаимодействие между Service и Tray;
- Windows Tray UI;
- окно сопряжения/регистрации устройства;
- автоматизированный контур тестирования Agent.

Текущий процесс регистрации создаёт запрос на регистрацию в Backend и отображает регистрационный код в Tray UI. Backend остаётся источником истины для состояния регистрации и решения об одобрении. Поллинг состояния одобрения, окончательная привязка устройства, heartbeat, выполнение команд и применение политик ещё не входят в версию 0.1.1.

## Архитектура

```text
Windows
   │
   ├── Device Agent Service
   │      ├── сбор идентификаторов
   │      ├── BackendClient
   │      ├── RegistrationCoordinator
   │      └── Named Pipe IPC server
   │
   └── Device Agent Tray
          ├── Named Pipe IPC client
          └── Pairing Window

                 │
                 ▼
        Family Beacon Backend
        /device-registration/requests
```

Tray является пользовательским интерфейсом. Windows Service владеет runtime Agent и взаимодействует с Backend. Tray не обращается к Backend напрямую.

## Идентификация устройства

Agent собирает следующий набор идентификаторов:

- `component`: `device-agent`
- `version`: версия Agent (`0.1.1`)
- `platform`: `windows`
- `windows_machine_guid`: Windows `MachineGuid`
- `hostname`: имя компьютера Windows
- `os_user_sid`: SID пользователя Windows
- `os_username`: имя пользователя Windows
- `os_session_identity`: информация о текущей Windows-сессии

`windows_machine_guid` является идентификатором устройства. `hostname` имеет информационный характер и не используется как идентификатор устройства.

## Локальные учётные данные Agent

Agent имеет механизм работы с локальным секретом установки, который является основой для аутентифицированной установки/первоначальной инициализации Agent:

- префикс секрета: `fb_agent_`;
- генерируется с использованием Python `secrets`;
- хранится в JSON по пути `%PROGRAMDATA%\FamilyBeacon\agent_credentials.json`;
- при необходимости используется резервный путь `%USERPROFILE%\.family_beacon\agent_credentials.json`;
- запись выполняется через временный файл с последующей атомарной заменой.

В текущем runtime-процессе версии 0.1.1 Agent не хранит Backend access token, refresh token или приватные ключи.

## Взаимодействие с Backend

Agent использует синхронный HTTP-клиент на базе стандартной библиотеки Python.

Текущие операции Backend:

- `POST /agent-installations/bootstrap`
- `POST /device-registration/requests`
- `GET /device-registration/requests/{request_id}`
- `POST /device-registration/cancel`

В текущем runtime используются операции создания и отмены запроса на регистрацию. Endpoint получения состояния уже присутствует в Backend-клиенте и предназначен для следующего этапа жизненного цикла регистрации.

URL Backend настраивается через:

```text
FAMILY_BEACON_BACKEND_URL
```

Значение по умолчанию для локальной разработки:

```text
http://127.0.0.1:8000
```

## Процесс регистрации в версии 0.1.1

```text
Tray
  │
  │ registration.start
  ▼
Agent Service
  │
  │ POST /device-registration/requests
  ▼
Backend
  │
  │ request_id + registration_code + expires_at
  ▼
Agent Service
  │
  ▼
Tray
  │
  └── отображает регистрационный код
```

Пользователь может отменить локальную попытку регистрации через Tray. Запрос на отмену передаётся из Tray в Service через локальный IPC, после чего Service очищает своё локальное состояние регистрации.

## Windows Service

Agent содержит Windows Service с именем:

```text
FamilyBeaconDeviceAgent
```

Отображаемое имя:

```text
Family Beacon Device Agent
```

Взаимодействие с Service Control Manager выполняется через `pywin32`. Сам Service является тонким адаптером вокруг `AgentRuntime`.

## Tray UI

Tray-приложение использует **PySide6** и взаимодействует с Windows Service через слой Named Pipe IPC.

В текущей версии Tray предоставляет:

- иконку Family Beacon в системном трее;
- запуск регистрации;
- отображение регистрационного кода;
- отмену регистрации;
- перезапуск Tray;
- выход из Tray.

Tray и Service являются отдельными процессами. Закрытие Tray не останавливает Windows Service.

## Локальный IPC

Agent использует Windows Named Pipe:

```text
\\.\pipe\family-beacon
```

Для IPC используется `multiprocessing.connection` с `AF_PIPE` и ключом аутентификации приложения.

Текущие типы сообщений:

- `status`
- `registration.start`
- `registration.cancel`

Сообщения представляют собой JSON-объекты с разделением сообщений по символу новой строки и ограничением максимального размера сообщения.

## Состояние регистрации

Текущий `RegistrationCoordinator` отслеживает:

- `request_id`
- `registration_code`
- `created_at`
- `expires_at`

Текущий жизненный цикл:

```text
IDLE
  │
  ├── registration.start
  ▼
REGISTRATION ACTIVE
  │
  ├── cancel ──► IDLE
  └── expiration ──► inactive
```

Следующий этап жизненного цикла — заставить Service отслеживать состояние регистрации в Backend и переводить локальный Agent через состояния одобрения, отклонения, истечения срока, отмены и успешной привязки устройства.

## Конфигурация runtime

Текущие значения по умолчанию:

| Параметр | Значение по умолчанию |
|---|---|
| Версия Agent | `0.1.1` |
| Окружение | `local` |
| Уровень логирования | `INFO` |
| URL Backend | `http://127.0.0.1:8000` |
| Интервал опроса регистрации | `10` секунд |

Интервал опроса регистрации можно изменить через:

```text
FAMILY_BEACON_PAIRING_POLL_INTERVAL_SECONDS
```

Значение должно быть положительным целым числом.

## Запуск Agent

Из корневой директории репозитория в Windows.

### Основное приложение

```text
python -m agent.device_agent.main
```

### Tray

```text
python -m agent.device_agent.tray.tray
```

### Windows Service

Точка входа Service:

```text
python -m agent.device_agent.service.service
```

Установка, запуск, остановка и другие команды управления Service Control Manager передаются в `pywin32`.

## Тесты

Тесты Agent изолированы в:

```text
agent/tests_agent
```

Запуск из корневой директории репозитория в Windows:

```text
python -m pytest agent/tests_agent -q
```

Контур тестирования Agent покрывает:

- конфигурацию;
- bootstrap credentials;
- сбор идентификаторов Windows;
- состояние регистрации;
- работу Backend-клиента;
- IPC Service runtime;
- работу Named Pipe server/client;
- работу окна сопряжения;
- работу Tray.

## Платформа

Device Agent работает **только в Windows**.

Backend и Telegram Bot остаются платформонезависимыми; сам Agent зависит от Windows API и компонентов runtime, специфичных для Windows.

## Текущие ограничения

Версия 0.1.1 пока не реализует:

- завершение регистрации после одобрения родителем;
- автоматический опрос/переход состояния registration request в `AgentRuntime`;
- окончательную привязку устройства к ребёнку после одобрения;
- постоянное хранение состояния зарегистрированного устройства;
- heartbeat;
- получение и выполнение команд;
- применение политик;
- передачу информации об использовании устройства;
- hardware fingerprinting;
- автоматический механизм установки/обновления Windows Service.

Это последующие этапы жизненного цикла и они намеренно не представлены как уже реализованная функциональность версии 0.1.1.

## Границы безопасности

Agent разделяет ответственность между процессами:

- Windows Service владеет runtime и взаимодействием с Backend.
- Tray отвечает за пользовательский интерфейс.
- Named Pipe IPC является границей локального взаимодействия.
- Backend остаётся источником истины для регистрации и состояния устройства.
- Windows MachineGuid идентифицирует устройство; hostname имеет информационный характер.
- Временные/локальные учётные данные хранятся вне системы контроля версий.

## Версия

Текущая версия Agent: **0.1.1**
