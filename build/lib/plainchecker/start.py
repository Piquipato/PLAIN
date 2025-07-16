try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
    from plainchecker.check import check
    from plainchecker.server import DaemonProcess
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
    from check import check
    from server import DaemonProcess
from datetime import datetime
import typing as tp
import logging
import click
import os


@click.command(
    help="Start check-in server to check in automatically with a given frequency",
    name="start",
)
@click.option(
    "frequency",
    "--frequency", "-f",
    type=float,
    default=24,
    help="How often do you want the bot to check-in " \
        "the users? (in hours, default: 24)"
)
@click.option(
    "extra_time_mean",
    "--extra-time-mean", "-em",
    type=float,
    default=5,
    help="How many extra minutes on average do you want the machine to add" \
        "to your check-in schedule? (default: 5)"
)
@click.option(
    "extra_time_std",
    "--extra-time-std", "-es",
    type=float,
    default=5,
    help="Tune out the std of extra minutes the machine adds" \
        "to your check-in schedule (default: 1)"
)
def start(
    frequency: float = 24, # hours
    extra_time_mean: float = 5,  # mins
    extra_time_std: float = 1,  # mins
):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    logger = setup_logging(
        log_cmd=True,
        log_level=10,
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_start_{timestamp}.log"
        )
    )
    logger.info("Starting the check-in server...")
    thr = DaemonProcess(
        name = f"CheckInServer_{timestamp}",
        target = check,
        kwargs = dict(
            extra_time_mean=extra_time_mean if extra_time_mean > 0 else 1,
            extra_time_std=extra_time_std if extra_time_std > 0  else 1,
        ),
        frequency=(frequency*60),
    )
    thr.start()
    logger.info(f"Started check-in server with frequency {frequency}h!")


if __name__ == '__main__':
    start()