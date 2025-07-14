from plainchecker.server import DaemonProcess
from target import target
import threading




if __name__ == "__main__":
    thr = DaemonProcess(
        name="TestDaemon",
        target=target,
        frequency=3/60,
    )
    thr.start()
    print("Daemon started")