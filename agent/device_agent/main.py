from .api import DeviceAgentAPI
from .worker import DeviceAgentWorker


def main():
    api = DeviceAgentAPI()
    worker = DeviceAgentWorker(api=api)

    print("========================================")
    print("       FAMILY BEACON DEVICE AGENT")
    print("========================================")

    worker.run()


if __name__ == "__main__":
    main()
