try:
    from plainchecker.logger import setup_logging
except ModuleNotFoundError:
    from logger import setup_logging
from functools import wraps
import typing as tp
import subprocess
import contextlib
import tempfile
import textwrap
import logging
import inspect
import socket
import pickle
import time
import sys
import os
import io


HOST = '127.0.0.1' # Localhost
PORT = 21201
TIMESTAMP = time.strftime("%Y%m%d%H%M%S", time.localtime())


def send_command(
    command: str,
    host: str = HOST,
    port: int = PORT,
    timeout: float = 0.5,
):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout) 
        sock.connect((host, port))
        data = pickle.dumps(command)
        sock.sendall(data)
        response = sock.recv(1024)
        return pickle.loads(response)


class DaemonProcess:
    
    def __init__(
        self,
        name: str = "DaemonProcess",
        host: str = HOST,
        port: int = PORT,
        target: tp.Callable = None,
        frequency: float = 15, # mins
        log_level: str = "DEBUG",
        log_file: str = os.path.abspath(f"logs/daemon-{TIMESTAMP}.log"),
        args: tp.Union[tp.List, tp.Tuple] = (),
        kwargs: tp.Dict[str, tp.Any] = {},
    ):
        self.log_level = log_level
        self.log_file = log_file
        self.running = False
        self.name = name
        self.host = host
        self.port = port
        self.target = target
        self.frequency = frequency * 60
        self.args = args
        self.kwargs = kwargs


    @staticmethod
    def _wrap_target(
        target: tp.Callable,
        logger: logging.Logger,
    ):
        @wraps(target)
        def wrapper(*args, **kwargs):
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                result = target(*args, **kwargs)
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()
            if stdout_output:
                logger.info(stdout_output)
            if stderr_output:
                logger.error(stderr_output)
            return result
        return wrapper

    setup_logging = staticmethod(setup_logging)

    def _run(
        self
    ):
        self.logger = self.setup_logging(
            log_level=self.log_level,
            log_file=self.log_file,
            log_cmd=True,
            log_format="[%(asctime)s | %(name)s | %(levelname)s]: %(message)s",
        )
        with socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM
        ) as sock:
            sock.bind((self.host, self.port))
            sock.settimeout(self.frequency)
            sock.listen()
            self.running = True
            self.logger.info(f"Daemon listening on {self.host}:{self.port}")
            while self.running:
                try:
                    conn, addr = sock.accept()
                    with conn:
                        self.logger.info(f"Connection from {addr}")
                        data = conn.recv(1024)
                        if not data:
                            continue
                        command = pickle.loads(data)
                        self.logger.info(f"Received command: {command}")
                        if command == "stop":
                            self.running = False
                            response = "Stopping daemon"
                            conn.sendall(pickle.dumps(response))
                            self.logger.info(response)
                            break
                        elif command == "ping":
                            conn.sendall(pickle.dumps("pong"))
                        else:
                            response = f"Command '{command}' received, ignoring..."
                            conn.sendall(pickle.dumps(response))
                except socket.timeout:
                    self.logger.info(f"Running target function {self.target.__name__}")
                    if not inspect.isbuiltin(self.target):
                        sig = inspect.signature(self.target)
                        bound = sig.bind_partial(*self.args, **self.kwargs)
                        bound.apply_defaults()
                        self.logger.info(f"Arguments: {bound.args}")
                        self.logger.info(f"Keyword arguments: {bound.kwargs}")
                        self.target = self._wrap_target(self.target, self.logger)
                        self.target(*bound.args, **bound.kwargs)
                    else:
                        self.logger.info(f"Arguments: {self.args}")
                        self.logger.info(f"Keyword arguments: {self.kwargs}")
                        self.target = self._wrap_target(self.target, self.logger)
                        self.target(*self.args, **self.kwargs)
    

    def store(self):
        script = tempfile.mkstemp(suffix=".py")
        with open(script[1], "w") as f:
            f.write(textwrap.dedent("""
                import sys, os
                sys.path.insert(0, "{libpath}")
                sys.path.insert(0, "{cwd}")

                import pickle
                import argparse
                import logging
                import multiprocessing
                                    
                if __name__ == "__main__":
                    parser = argparse.ArgumentParser(description="Daemon Process")
                    parser.add_argument("--server", type=str, required=True, help="Server address")
                    args = parser.parse_args()
                    with open(args.server, "rb") as f:
                        try:
                            daemon = pickle.load(f)
                        except Exception as e:
                            print(args.server)
                            raise e
                    logger = daemon.setup_logging(
                        log_level=daemon.log_level,
                        log_file=daemon.log_file,
                        log_cmd=False,
                        log_format="[%(asctime)s | %(name)s | %(levelname)s]: %(message)s",
                    )
                    logger.info("Daemon process with PID: %s", os.getpid())
                    daemon._run()
                    
                    # process = multiprocessing.Process(
                    #     target=daemon._run,
                    #     name=daemon.name,
                    # )
                    # process.start()
                    # logger.info("Daemon process with name %s started with PID: %s", daemon.name, process.pid)
            """.format(
                libpath=os.path.abspath(os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    ".."
                )).replace("\\", "\\\\"),
                cwd=sys.modules[self.target.__module__].__file__.replace("\\", "\\\\"),
            )))
        return script[1]


    def start(self):
        # self.thread = multiprocessing.Process(
        #     target=self._run,
        #     name=self.name,
        # )
        # self.thread.start()
        # print(self.thread.pid)
        # print(self.thread.is_alive())
        self_pkl = tempfile.mkstemp(suffix=".pkl")
        with open(self_pkl[1], "wb") as f:
            pickle.dump(self, f)
        script = self.store()
        command = [
            "python",
            script,
            "--server",
            self_pkl[1],
        ]
        print(" ".join(command))
        subprocess.Popen(command)


    def stop(
        self,
        host: str = HOST,
        port: int = PORT,
    ):
        if hasattr(self, 'thread'):
            self.send_command("stop", self.host, self.port)
            self.thread.join()
            self.logger.info(f"Daemon {self.name} stopped.")
        else:
            self.send_command("stop", host, port)
            self.logger.info(f"Daemon stopped on {host}:{port}.")