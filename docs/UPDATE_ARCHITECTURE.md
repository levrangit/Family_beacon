# Family Beacon — Update Architecture

## Назначение

Этот документ фиксирует архитектурные принципы будущей системы обновлений Family Beacon.

Документ описывает архитектурные ограничения и направления проектирования. Он **не является реализацией Update Service или updater**.

## 1. Общая модель

Family Beacon состоит из нескольких независимо развиваемых компонентов. Каждый компонент должен проектироваться так, чтобы в будущем его можно было независимо версионировать, обновлять, проверять после обновления и при необходимости откатывать.

Общий жизненный цикл релиза:

```text
feature / fix
    ↓
develop
    ↓
CI + tests
    ↓
PR
    ↓
main
    ↓
Release
    ↓
Update Service
    ↓
Update Manifest
    ↓
components
    ↓
verification / installation / health check
    ↓
SUCCESS / ROLLBACK
```

## 2. Независимые версии компонентов

Следующие компоненты должны иметь возможность иметь собственные версии:

- Backend
- Telegram Bot
- Frontend
- Device Agent
- Update Service

Версия продукта и версии компонентов не обязаны совпадать.

Пример:

```text
Family Beacon v0.5.0
Backend       0.5.0
Telegram      0.5.0
Frontend      0.4.2
Device Agent  0.3.1
Update        0.2.0
```

## 3. GitHub и релизы

GitHub остаётся источником исходного кода, Git-тегов и Release-метаданных.

Работающие компоненты не должны использовать Git-репозиторий как непосредственный API обновлений.

Предполагаемый поток:

```text
GitHub
  ↓
Release Pipeline
  ↓
GitHub Release
  ↓
Update Service
  ↓
components
```

## 4. Update Service

Update Service должен быть отдельным серверным компонентом.

Его задача — предоставлять авторизованным компонентам информацию о доступных обновлениях и управлять политикой доставки.

Device Agent должен взаимодействовать с Backend / Update Service, а не напрямую с GitHub.

## 5. Update Manifest

Информация об обновлении должна передаваться через формализованный Update Manifest.

Manifest в будущем должен описывать как минимум:

- компонент;
- целевую версию;
- совместимость;
- пакет обновления;
- URL доставки;
- SHA-256 checksum;
- цифровую подпись;
- канал обновления;
- требования к минимальной поддерживаемой версии.

Точный формат Manifest будет определён отдельно при реализации Update Service.

## 6. Безопасность пакета

Компонент не должен принимать команду вида «скачай этот URL и запусти файл» без проверки.

Минимальная архитектурная цепочка проверки:

```text
Update Manifest
      ↓
Package URL
      ↓
Download
      ↓
SHA-256 verification
      ↓
Digital signature verification
      ↓
Install
```

SHA-256 проверяет целостность пакета. Цифровая подпись должна подтверждать доверенное происхождение пакета.

## 7. Установка Device Agent

Обновление Device Agent не должно быть простым перезаписыванием работающего файла.

Предполагаемый процесс:

```text
Agent OLD
    ↓
download NEW
    ↓
verify
    ↓
prepare
    ↓
stop OLD
    ↓
install NEW
    ↓
start NEW
    ↓
health check
```

В Windows production-агент предполагается как `FamilyBeaconAgent.exe`, работающий как Windows Service. Отдельный updater должен отвечать за безопасную замену работающего Agent.

## 8. Health Check

После установки новая версия должна пройти Health Check до того, как будет считаться активной.

Health Check должен подтверждать как минимум:

- запуск новой версии;
- успешную аутентификацию;
- подключение к Backend;
- отправку heartbeat;
- получение команд;
- выполнение базовой операции Agent.

## 9. Rollback

Rollback является частью архитектуры обновления.

```text
ACTIVE
   ↓
CANDIDATE
   ↓
HEALTH CHECK
   ├── OK → ACTIVE
   └── FAIL → ROLLBACK → PREVIOUS
```

Система должна сохранять возможность вернуться к предыдущей рабочей версии.

Результат rollback должен быть отдельно фиксируемым событием, а не теряться за финальным состоянием версии.

## 10. Состояния обновления

Будущая система должна поддерживать явную state machine:

```text
AVAILABLE
   ↓
REQUESTED
   ↓
DOWNLOADING
   ↓
VERIFYING
   ↓
INSTALLING
   ↓
RESTARTING
   ↓
HEALTH_CHECK
   ↓
SUCCESS
```

Возможные состояния ошибки:

- DOWNLOAD_FAILED
- VERIFY_FAILED
- INSTALL_FAILED
- HEALTH_CHECK_FAILED
- ROLLING_BACK
- ROLLED_BACK

## 11. История обновлений

Backend должен в будущем хранить историю обновлений Device Agent.

Концептуальная модель:

```text
device
current_version
target_version
status
started_at
completed_at
error
attempt
```

Это позволит отличать успешное обновление, неудачную установку и rollback.

## 12. Совместимость версий

Backend и Device Agent не должны предполагать, что любая версия совместима с любой другой.

В будущем должна существовать Compatibility Matrix.

Пример:

```text
Backend 0.4.x + Agent 0.3.x = supported
Backend 0.5.x + Agent 0.3.x = supported
Backend 0.5.x + Agent 0.2.x = warning
Backend 0.6.x + Agent 0.2.x = unsupported
```

При необходимости должны поддерживаться параметры:

- `minimum_supported_agent`;
- `recommended_agent`;
- `latest_agent`.

## 13. Проверка обновлений через heartbeat

Heartbeat Device Agent уже является каналом регулярного взаимодействия с Backend.

В будущем через этот механизм могут передаваться:

- текущая версия Agent;
- информация о доступном обновлении;
- состояние текущего обновления;
- результат Health Check.

При этом наличие доступного обновления не должно автоматически означать немедленную установку. Решение должно приниматься Backend / Update Policy.

## 14. Update Policy

Backend / Update Policy отвечает за решение:

- кому доступно обновление;
- какую версию разрешено устанавливать;
- когда выполнять обновление;
- какой канал использовать;
- можно ли выполнять rollout.

Администратор не должен напрямую управлять файлами обновления Device Agent через Telegram.

## 15. Staged Rollout

Production-обновления должны поддерживать поэтапную доставку.

Предполагаемая схема:

```text
Release
   ↓
Canary
   ↓
small device group
   ↓
Health Check
   ↓
25%
   ↓
50%
   ↓
100%
```

При проблемах rollout должен останавливаться.

## 16. Каналы обновлений

Архитектура должна предусматривать каналы:

- Stable
- Beta
- Canary

Конкретная политика использования каналов будет определена при реализации rollout-механизма.

## 17. Supabase

Supabase schema updates не являются обычным обновлением приложения.

Изменения схемы выполняются через migration workflow проекта.

```text
Application Release
    ├── Backend
    ├── Telegram Bot
    ├── Frontend
    └── Device Agent

Database
    ↓
Migration Workflow
```

Действующие правила проекта для миграций остаются обязательными.

## 18. Telegram Bot

Telegram Bot может:

- отображать состояние обновления;
- уведомлять администратора о результате;
- отображать ошибки и состояние компонентов.

Telegram Bot не должен быть механизмом доставки исполняемых пакетов обновления.

## 19. Граница текущего этапа

На текущем этапе проекта:

- Update Service не реализуется;
- updater Device Agent не реализуется;
- rollout-механизм не реализуется;
- rollback-механизм не реализуется.

Сейчас эти требования используются как архитектурные ограничения при разработке остальных компонентов.

## 20. Главный архитектурный принцип

> Разработка производит Release. Release запускает процесс обновления. Update Service доставляет Release. Компонент самостоятельно проверяет, устанавливает и подтверждает новую версию. При неуспехе система должна иметь возможность выполнить Rollback.

Эти принципы должны учитываться при дальнейшем проектировании Backend, Device Agent, Frontend и Telegram Bot, чтобы последующая реализация системы обновлений не потребовала фундаментальной переделки архитектуры.
