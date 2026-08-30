from .api import DeviceAgentAPI
from .worker import DeviceAgentWorker


def main():
    api = DeviceAgentAPI()
    worker = DeviceAgentWorker(api=api)

    print("========================================")
    print("       FAMILY BEACON DEVICE AGENT")
    print("========================================")

    try:
        worker.run()
    except KeyboardInterrupt:
        print()
        print("DEVICE AGENT STOPPED")


if __name__ == "__main__":
    main()
