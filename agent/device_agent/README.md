# Device Agent — pairing window

`device_pairing_window.py` contains the standalone Agent-side registration window.

## Current stage

This component is a UI implementation based on the existing Family Beacon web
`AddDeviceModal` visual design. It is intentionally decoupled from Supabase,
Telegram, and the backend registration flow.

The device platform is determined by the Agent, so the user does not select an
operating system in this window. The pairing code is supplied to
`show_pairing()` or `open_device_pairing_window()` by the Agent; no real or fixed
code is generated in this UI.

## Integration contract

The Agent's **«Регистрация»** action should call:

```python
open_device_pairing_window(
    root,
    child_name=child_name,
    pairing_code=current_pairing_code,
    on_complete=handle_pairing_complete,
)
```

`handle_pairing_complete(device_name, pairing_code)` is the integration point
for the future registration-request flow. The UI itself does not create a
Supabase `devices` record and does not authenticate a device.
