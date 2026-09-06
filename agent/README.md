# Family Beacon Device Agent 0.1.0

Minimal Windows-only Device Agent MVP.

## Purpose

The 0.1.0 Agent establishes the local identity collection boundary. It does not register a device, authenticate against the Backend, pair with a child, or manage policies.

## Current identity payload

- `component`: `device-agent`
- `version`: `0.1.0`
- `platform`: `windows`
- `windows_machine_guid`
- `hostname`
- `os_user_sid`
- `os_username`
- `os_session_identity`

The hostname is informational and is not used as device identity.

## Run

From the repository root on Windows:

```text
python -m device_agent.main
```

## Tests

From the repository root:

```text
pytest agent/tests
```

The Agent currently uses only Python standard-library modules.

## Explicitly out of scope for 0.1.0

- Backend API communication
- Device registration
- Device credentials, access tokens, refresh tokens or private keys
- Pairing and approval
- Child binding
- Heartbeat
- Commands and command execution
- Policy enforcement
- Hardware fingerprinting
- Windows Service installation
- Persistent sensitive local state
