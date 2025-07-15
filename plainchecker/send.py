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
    help="Send a command to the PlainChecker server.",
    name="send",
)
@click.argument(
    "command",
    type=str,
    metavar="COMMAND",
    required=True,
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
@click.option(
    "--log-level", "-l",
    type=click.Choice(list(LOG_LEVELS.keys()), case_sensitive=False),
    default="INFO",
    help="Logging level for the command. Default is INFO."
)
def send(
    command: str,
    host: str = HOST,
    port: int = PORT,
    timeout: float = 0.5,
    log_level: str = "INFO",
):
    logger = setup_logging(
        log_level=LOG_LEVELS[log_level],
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_send_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
    )
    logger.info(f"Sending command: {command} to {host}:{port} with timeout {timeout} seconds...")
    try:
        response = send_command(command, host=host, port=port, timeout=timeout)
        logger.info(f"Received response: {response}")
    except Exception as e:
        logger.error(f"Failed to send command: {e}")
        logger.debug(traceback.format_exc())
        logger.info("No response received.")


if __name__ == "__main__":
    send()