import typing as tp
import threading
import socket
import pickle
import time


HOST = '127.0.0.1' # Localhost
PORT = 21201


class DaemonProcess(threading.Thread):
    
    def __init__(self, target: tp.Callable = None, *args, **kwargs):
        super().__init__(daemon=True)
        self.target = target
        self.args = args
        self.kwargs = kwargs


    def start(self, target = None, *args, **kwargs):
        if target is None:
            self.target = target
            self.args = args
            self.kwargs = kwargs
        self.target(*self.args, **self.kwargs)
    

    def stop(self):
        raise NotImplementedError("Stop method is not implemented for DaemonProcess.")