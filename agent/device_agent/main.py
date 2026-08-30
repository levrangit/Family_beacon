import time

from .api import DeviceAgentAPI
from .auth import DeviceAuth
from .config import POLL_INTERVAL_SECONDS
from .worker import DeviceAgentWorker


def main():
    api = DeviceAgentAPI()
    auth = DeviceAuth(api)
    worker = DeviceAgentWorker(api=api)

    print("========================================")
    print("       FAMILY BEACON DEVICE AGENT")
    print("========================================")

    while True:
        try:
            print("AUTHENTICATING...")

            device_id = auth.authenticate()

            print(f"DEVICE AUTH OK: {device_id}")
            print(
                f"POLL INTERVAL: "
                f"{POLL_INTERVAL_SECONDS}s"
            )
            print("DEVICE AGENT RUNNING")
            print("Press Ctrl+C to stop.")
            print()

            while True:
                try:
                    processed = worker.run_once()

                    if processed:
                        print("COMMAND CYCLE COMPLETED")
                    else:
                        print("NO PENDING COMMANDS")

                except Exception as exc:
                    print(f"WORKER ERROR: {exc}")

                time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print()
            print("DEVICE AGENT STOPPED")
            break

        except Exception as exc:
            print(f"DEVICE AGENT ERROR: {exc}")
            print("RETRYING AUTHENTICATION IN 5 SECONDS...")
            time.sleep(5)


if __name__ == "__main__":
    main()
