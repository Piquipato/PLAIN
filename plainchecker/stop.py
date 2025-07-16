try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
    from plainchecker.server import send_command, HOST, PORT
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
    from server import send_command, HOST, PORT
from datetime import datetime
import traceback
import click
import os


@click.command(
    help="Stop a PlainChecker server.",
    name="stop",
)
@click.option(
    "--host", "-H",
    type=str,
    default=HOST,
    help="Host address of the PlainChecker server. Default is 'localhost'."
)
@click.option(
    "--port", "-P",
    type=int,
    default=PORT,
    help="Port number of the PlainChecker server. Default is 5000."
)
@click.option(
    "--timeout", "-t",
    type=float,
    default=0.5,
    help="Timeout for the server response in seconds. Default is 5 seconds."
)
def stop(
    host: str = HOST,
    port: int = PORT,
    timeout: float = 0.5
):
    logger = setup_logging(
        log_cmd=True,
        log_level=10,
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_stop_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
    )
    logger.info(f"Stopping the server at {host}:{port}...")
    try:
        response = send_command(
            "stop",
            host,
            port,
            timeout
        )
        logger.info("Server stopped, exiting...")
    except Exception as e:
        logger.error(f"An error occured during execution: {e}")
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    stop()