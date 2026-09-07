"""Windows Service entry point for the Family Beacon Device Agent."""

from __future__ import annotations

import servicemanager
import win32event
import win32service
import win32serviceutil

from .runtime import AgentRuntime


class DeviceAgentService(win32serviceutil.ServiceFramework):
    """Thin adapter between Windows SCM and the AgentRuntime."""

    _svc_name_ = "FamilyBeaconDeviceAgent"
    _svc_display_name_ = "Family Beacon Device Agent"
    _svc_description_ = "Family Beacon background Device Agent service."

    def __init__(self, args: list[str]) -> None:
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.runtime = AgentRuntime()

    def SvcStop(self) -> None:
        """Handle a stop request from Windows Service Control Manager."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.runtime.request_stop()
        win32event.SetEvent(self.stop_event)

    def SvcShutdown(self) -> None:
        """Handle a Windows shutdown notification."""
        self.SvcStop()

    def SvcDoRun(self) -> None:
        """Start the runtime and wait until Windows requests a stop."""
        servicemanager.LogInfoMsg(
            f"{self._svc_name_}: service starting"
        )
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        try:
            self.runtime.start()
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        except Exception as exc:
            servicemanager.LogErrorMsg(
                f"{self._svc_name_}: service failed: {exc!r}"
            )
            raise
        finally:
            self.runtime.stop()
            servicemanager.LogInfoMsg(
                f"{self._svc_name_}: service stopped"
            )


def main() -> None:
    """Delegate install/start/stop and other commands to pywin32."""
    win32serviceutil.HandleCommandLine(DeviceAgentService)


if __name__ == "__main__":
    main()
