# Family Beacon Device Agent 0.1.1

Windows-only Device Agent for Family Beacon.

## Purpose

The Device Agent runs on the child's Windows computer and provides the local device boundary between Windows, the Family Beacon Backend, and the user-facing Tray UI.

Version **0.1.1** establishes the following working foundation:

- Windows device identity collection
- local Agent configuration
- persistent local Agent installation secret generation/storage
- communication with the Family Beacon Backend
- creation of a device registration request
- local registration state management
- Windows Service runtime
- authenticated local IPC between the Service and Tray
- Windows Tray UI
- device pairing/registration window
- automated Agent test contour

The current registration flow creates a Backend registration request and displays the registration code in the Tray UI. The Backend remains the authority for registration state and approval. Full approval polling, final device binding, heartbeat, command execution, and policy enforcement are not yet part of version 0.1.1.

## Architecture

```text
Windows
   │
   ├── Device Agent Service
   │      ├── identity collection
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

The Tray is a user interface. The Windows Service owns the Agent runtime and communicates with the Backend. The Tray does not call the Backend directly.

## Device identity

The Agent collects the following identity payload:

- `component`: `device-agent`
- `version`: Agent version (`0.1.1`)
- `platform`: `windows`
- `windows_machine_guid`: Windows `MachineGuid`
- `hostname`: Windows hostname
- `os_user_sid`: Windows user SID
- `os_username`: Windows username
- `os_session_identity`: current Windows session information

`windows_machine_guid` is the device identity. The hostname is informational and is not used as the device identity.

## Local Agent credentials

The Agent has a local installation-secret mechanism used as the foundation for authenticated Agent installation/bootstrap:

- secret prefix: `fb_agent_`
- generated with Python `secrets`
- stored as JSON under `%PROGRAMDATA%\FamilyBeacon\agent_credentials.json`
- falls back to `%USERPROFILE%\.family_beacon\agent_credentials.json` when necessary
- writes through a temporary file followed by atomic replacement

The Agent does not store Backend access tokens, refresh tokens, or private keys as part of the current 0.1.1 runtime flow.

## Backend communication

The Agent uses a synchronous standard-library HTTP client.

Current Backend operations:

- `POST /agent-installations/bootstrap`
- `POST /device-registration/requests`
- `GET /device-registration/requests/{request_id}`
- `POST /device-registration/cancel`

The current runtime actively uses the registration-request creation and cancellation operations. The status endpoint is already available in the Backend client and is reserved for the next registration lifecycle step.

Backend URL is configured through:

```text
FAMILY_BEACON_BACKEND_URL
```

Default local value:

```text
http://127.0.0.1:8000
```

## Registration flow in 0.1.1

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
  └── displays registration code
```

The user can cancel the local registration attempt through the Tray. Cancellation is sent from the Tray to the Service over local IPC, and the Service clears its local registration state.

## Windows Service

The Agent includes a Windows Service named:

```text
FamilyBeaconDeviceAgent
```

Display name:

```text
Family Beacon Device Agent
```

The Service Control Manager is handled through `pywin32`. The Service is a thin adapter around `AgentRuntime`.

## Tray UI

The Tray application uses **PySide6** and communicates with the Windows Service through the Named Pipe IPC layer.

The Tray currently provides:

- Family Beacon system-tray icon
- registration start
- registration code display
- registration cancellation
- Tray restart
- Tray exit

The Tray and Service are separate processes. Closing the Tray does not stop the Windows Service.

## Local IPC

The Agent uses a Windows Named Pipe:

```text
\\.\pipe\family-beacon
```

IPC uses `multiprocessing.connection` with `AF_PIPE` and an application auth key.

Current message types:

- `status`
- `registration.start`
- `registration.cancel`

Messages are JSON objects separated by newline framing and are subject to a maximum message size.

## Registration state

The local `RegistrationCoordinator` currently tracks:

- `request_id`
- `registration_code`
- `created_at`
- `expires_at`

Current lifecycle:

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

The next lifecycle step is to make the Service observe the Backend registration status and transition the local Agent through approval, rejection, expiration, cancellation, and successful device binding states.

## Runtime configuration

Current defaults:

| Setting | Default |
|---|---|
| Agent version | `0.1.1` |
| Environment | `local` |
| Log level | `INFO` |
| Backend URL | `http://127.0.0.1:8000` |
| Registration poll interval | `10` seconds |

Registration polling interval can be changed with:

```text
FAMILY_BEACON_PAIRING_POLL_INTERVAL_SECONDS
```

The value must be a positive integer.

## Running the Agent

From the repository root on Windows.

### Main application

```text
python -m agent.device_agent.main
```

### Tray

```text
python -m agent.device_agent.tray.tray
```

### Windows Service

The Service entry point is:

```text
python -m agent.device_agent.service.service
```

Installation, start, stop, and other Service Control Manager commands are delegated to `pywin32`.

## Tests

Agent tests are isolated under:

```text
agent/tests_agent
```

Run them from the repository root on Windows:

```text
python -m pytest agent/tests_agent -q
```

The Agent test contour covers:

- configuration
- bootstrap credentials
- Windows identity collection
- registration state
- Backend client behavior
- Service runtime IPC
- Named Pipe server/client behavior
- pairing window behavior
- Tray behavior

## Platform

The Device Agent is **Windows-only**.

The Backend and Telegram Bot remain platform-independent; the Agent itself depends on Windows APIs and Windows-specific runtime components.

## Current limitations

Version 0.1.1 does not yet implement:

- completion of registration after parent approval
- automatic polling/transition of the registration request in `AgentRuntime`
- final device binding to a child after approval
- persistent registered-device state
- heartbeat
- command retrieval and execution
- policy enforcement
- device usage reporting
- hardware fingerprinting
- automatic service installation/update mechanism

These are later lifecycle stages and are intentionally not represented as completed functionality in 0.1.1.

## Security boundaries

The Agent separates responsibilities between processes:

- Windows Service owns the runtime and Backend communication.
- Tray owns the user interface.
- Named Pipe IPC is the local communication boundary.
- Backend remains the authority for registration and device state.
- Windows MachineGuid identifies the device; hostname is informational.
- Temporary/local credentials are kept outside source control.

## Version

Current Agent version: **0.1.1**
