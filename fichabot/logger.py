from tabulate import tabulate
import functools
import traceback
import builtins
import inspect
import logging
import os


LOG_LEVELS = dict(sorted([
    (name, lvl) for name, lvl in logging._nameToLevel.items()
], key=lambda x: x[1]))

def setup_logging(
    log_level: int = 20,
    log_file: str = None,
    log_cmd: bool = True,
    log_format: str = '[%(asctime)s | %(levelname)s]: %(message)s'
):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    if not any(
        isinstance(handler, logging.StreamHandler)
        for handler in logger.handlers
    ) or log_cmd:
        stream = logging.StreamHandler()
        stream.setLevel(log_level)
        stream.setFormatter(formatter)
        logger.addHandler(stream)
    if not isinstance(log_file, type(None)):
        fileh = logging.FileHandler(filename=log_file)
        fileh.setLevel(log_level)
        fileh.setFormatter(formatter)
        logger.addHandler(fileh)


def track_open(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        original_open = builtins.open
        def open_logger(file, *a, **k):
            if isinstance(file, int):
                logging.debug(f"Opened file descriptor {file}")
            else:
                opened = os.path.abspath(file)
                logging.debug(f"Opened file {opened}")
            return original_open(file, *a, **k)
        builtins.open = open_logger
        try:
            result = func(*args, **kwargs)
        finally:
            builtins.open = original_open
        return result
    return wrapper
    

def log_step(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        runner = track_open(func)
        logging.debug(f"Running step {func.__name__}")
        prototype = inspect.signature(func)
        logging.debug(f"Prototype: {func.__name__}{prototype}")
        bound = prototype.bind(*args, **kwargs)
        bound.apply_defaults()
        params = [
            (k, v) for k, v in bound.arguments.items()
            if k not in ["args", "kwargs"]
        ]
        ag = bound.arguments.get("args")
        kw = bound.arguments.get("kwargs")
        if ag:
            params += [
                (f"args_{i}", ag[i]) for i in range(len(ag))
            ]
        if kw:
            params += [(k, v) for k, v in kw.items()]
        table = tabulate(
            params, headers=["Parameter", "Value"], tablefmt="pretty"
        )
        logging.debug(f"Arguments:\n{table}")
        try:
            return runner(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error while running step {func.__name__}")
            logging.error(f"Exception: {e}")
            logging.error(f"Traceback:\n{traceback.format_exc()}")
            raise e
    return wrapper