"""Windows identity collection for Device Agent 0.1.0."""

from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DeviceIdentity:
    """Identity information collected from the current Windows environment."""

    component: str
    version: str
    platform: str
    windows_machine_guid: str
    hostname: str
    os_user_sid: str
    os_username: str
    os_session_identity: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def get_windows_machine_guid() -> str:
    """Read the Windows MachineGuid from the registry."""

    if os.name != "nt":
        raise RuntimeError("Windows MachineGuid is available only on Windows")

    command = [
        "reg",
        "query",
        r"HKLM\SOFTWARE\Microsoft\Cryptography",
        "/v",
        "MachineGuid",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if "MachineGuid" in line:
            parts = line.split()
            if parts:
                return parts[-1].strip()

    raise RuntimeError("Windows MachineGuid was not found")


def get_os_user_sid() -> str:
    """Return the SID of the current Windows user."""

    if os.name != "nt":
        raise RuntimeError("Windows user SID is available only on Windows")

    username = os.environ.get("USERNAME")
    if not username:
        raise RuntimeError("USERNAME environment variable is not available")

    result = subprocess.run(
        ["whoami", "/user", "/fo", "csv", "/nh"],
        capture_output=True,
        text=True,
        check=True,
    )
    fields = [field.strip('"') for field in result.stdout.strip().split(",")]
    if len(fields) < 2 or not fields[1]:
        raise RuntimeError("Current Windows user SID was not found")
    return fields[1]


def get_os_session_identity() -> str:
    """Return the current Windows session identity."""

    username = os.environ.get("USERNAME")
    session_name = os.environ.get("SESSIONNAME")
    session_id = os.environ.get("SESSION_ID") or os.environ.get("SESSIONID")

    parts = [part for part in (username, session_name, session_id) if part]
    if not parts:
        raise RuntimeError("Windows session identity is not available")
    return "\\".join(parts)


def collect_identity(agent_version: str = "0.1.0") -> DeviceIdentity:
    """Collect the complete identity payload for the current Windows host."""

    if platform.system().lower() != "windows":
        raise RuntimeError("Device Agent 0.1.0 currently supports Windows only")

    return DeviceIdentity(
        component="device-agent",
        version=agent_version,
        platform="windows",
        windows_machine_guid=get_windows_machine_guid(),
        hostname=platform.node(),
        os_user_sid=get_os_user_sid(),
        os_username=os.environ.get("USERNAME", ""),
        os_session_identity=get_os_session_identity(),
    )
