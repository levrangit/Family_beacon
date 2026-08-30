from .api import DeviceAgentAPI


class DeviceAuth:
    def __init__(self, api: DeviceAgentAPI):
        self.api = api
        self.device_id: str | None = None

    def authenticate(self) -> str:
        response = self.api.authenticate()

        device_id = response.get("device_id")

        if not device_id:
            raise RuntimeError(
                "Backend did not return device_id"
            )

        self.device_id = str(device_id)

        return self.device_id
