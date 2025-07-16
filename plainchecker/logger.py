import logging

LOG_LEVELS = dict(sorted([
    (name, lvl) for name, lvl in logging._nameToLevel.items()
], key=lambda x: x[1]))


def setup_logging(
    log_level: int = 20,
    log_file: str = None,
    log_format: str = '[%(asctime)s | %(levelname)s] : %(message)s',
    log_cmd: bool = True,
):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    if not any(
        isinstance(handler, logging.StreamHandler)
        for handler in logger.handlers
    ) and log_cmd:
        stream = logging.StreamHandler()
        stream.setLevel(log_level)
        stream.setFormatter(formatter)
        logger.addHandler(stream)
    if not any(
        isinstance(handler, logging.StreamHandler)
        for handler in logger.handlers
    ) and not isinstance(log_file, type(None)):
        fileh = logging.FileHandler(filename=log_file)
        fileh.setLevel(log_level)
        fileh.setFormatter(formatter)
        logger.addHandler(fileh)
    return logger