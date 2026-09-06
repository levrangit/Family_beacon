# Device Agent — pairing window and Tray

`device_pairing_window.py` contains the standalone Agent-side registration window.
The Tray implementation lives under `tray/` and uses Python + PySide6.

## Current stage

The Device Agent Tray has a minimal working Windows-tested skeleton with the
original Family Beacon lighthouse SVG as its Tray icon.

Stage B adds a shared PySide6 visual system in `ui/theme.py`. Its tokens are
kept aligned with the existing frontend design tokens: Family Beacon blue,
light surfaces, neutral text, outlines, green secondary color, and the native
Windows `Segoe UI` font.

The Tray menu is intentionally lightweight and currently contains only:

- `Регистрация` — temporary Stage A notification;
- `Выйти` — closes the Tray process only.

There is still no Backend, Supabase, Telegram, IPC, or Windows Service
integration in this stage.

## Pairing window

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
