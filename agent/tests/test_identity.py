from agent.device_agent.identity import DeviceIdentity, get_os_session_identity


def test_identity_payload_shape() -> None:
    identity = DeviceIdentity(
        component="device-agent",
        version="0.1.0",
        platform="windows",
        windows_machine_guid="machine-guid",
        hostname="HOST",
        os_user_sid="S-1-5-21-test",
        os_username="child",
        os_session_identity="child\\Console\\1",
    )

    assert identity.to_dict() == {
        "component": "device-agent",
        "version": "0.1.0",
        "platform": "windows",
        "windows_machine_guid": "machine-guid",
        "hostname": "HOST",
        "os_user_sid": "S-1-5-21-test",
        "os_username": "child",
        "os_session_identity": "child\\Console\\1",
    }


def test_session_identity_uses_available_environment(monkeypatch) -> None:
    monkeypatch.setenv("USERNAME", "child")
    monkeypatch.setenv("SESSIONNAME", "Console")
    monkeypatch.setenv("SESSION_ID", "1")

    assert get_os_session_identity() == "child\\Console\\1"
