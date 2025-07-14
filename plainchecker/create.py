try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
from datetime import datetime, timedelta
import keyring
import logging
import getpass
import click
import json
import os

SEPARATORS = [",", ";", "-"]

def parse_exceptions(dates: str) -> list:
    for sep in SEPARATORS:
        if sep in dates:
            (start, end) = dates.split(sep)
            start = datetime.strptime(start.strip(), "%d/%m/%Y")
            end = datetime.strptime(end.strip(), "%d/%m/%Y")
            dates = [
                start + timedelta(days=i)
                for i in range((end - start).days + 1)
            ]
            return [datetime.strftime(date, "%d/%m/%Y") for date in dates]
    return [datetime.strptime(dates.strip(), "%d/%m/%Y")]


def parse_work_days(work_days: str) -> list:
    for sep in SEPARATORS:
        if sep in work_days:
            (start, end) = work_days.split(sep)
            return list(range(
                int(start.strip()),
                int(end.strip()) + 1
            ))
    return [int(work_days.strip())]


def parse_schedule(schedule: str) -> list:
    for sep in SEPARATORS:
        if sep in schedule:
            return list(schedule.split(sep))
    return ["09:00", "17:00"]


@click.command(
    help="Create a new user configuration for PlainChecker.",
    name="create",
)
@click.argument(
    "username",
    type=str,
    metavar="USERNAME",
    required=True,
)
@click.argument(
    "email",
    type=str,
    metavar="EMAIL",
    required=True,
)
@click.option(
    "--work-days", "-w",
    type=str,
    default=[],
    multiple=True,
    help="Work days for the user, e.g. '1-5' for Monday to Friday or 3 for Wednesday."
)
@click.option(
    "--exceptions", "-x",
    type=str,
    default=[],
    multiple=True,
    help="Exceptions for the user, e.g. '01/01/2023, 02/01/2023' or '01/01/2023-05/01/2023'."
)
@click.option(
    "--schedule", "-s",
    type=str,
    default="09:00,17:00",
    help="Schedule for the user, e.g. '09:00-17:00' for 9 AM to 5 PM."
)
@click.option(
    "--log-level", "-l",
    type=click.Choice(list(LOG_LEVELS.keys()), case_sensitive=False),
    default="INFO",
    help="Logging level for the user configuration. Default is INFO."
)
def create(
    username: str,
    email: str,
    work_days: str = "",
    exceptions: str = "",
    schedule: str = "",
    log_level: str = "INFO",
):
    config_file = os.path.join(
        CONFIG_DIR,
        f"{username}.json"
    )
    log_file = os.path.join(
        LOG_DIR,
        f"plainchecker_create_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    )
    logger = setup_logging(
        log_level=LOG_LEVELS.get(log_level.upper(), logging.INFO),
        log_file=log_file,
        log_cmd=True,
    )
    if os.path.exists(config_file) and \
        os.path.isfile(config_file):
        config_json = json.load(open(config_file, "r"))
        logger.info(f"Configuration file {config_file} already exists. Appending to it.")
    else:
        config_json = []
        logger.info(f"Creating new configuration file {config_file}.")
    if email in [conf.get("email") for conf in config_json]:
        logger.warning(f"Email {email} already exists in the configuration file!")
        logger.warning("Exiting without changes.")
        return
    else:
        exceptions_lst = [
            date for exc in exceptions for date in parse_exceptions(exc)
        ]
        work_days_lst = [
            day for wd in work_days for day in parse_work_days(wd)
        ]
        config_json.append(dict(
            username=username,
            email=email,
            work_days=work_days_lst if work_days_lst else [1, 2, 3, 4, 5],
            exceptions=exceptions_lst if exceptions_lst else [],
            schedule=parse_schedule(schedule) if schedule else ["09:00", "17:00"],
        ))
        logger.info(f"Adding new user {username} to the configuration file.")
        logger.info("Password will be set in the keyring.")
        setup = False
        while not setup:
            passwd = getpass.getpass("Enter your password: ")
            repass = getpass.getpass("Repeat your password: ")
            setup = passwd == repass
        keyring.set_password(
            "plainchecker",
            email,
            passwd
        )
    with open(config_file, "w") as f:
        json.dump(config_json, f, indent=4)
    logger.info("Done! Configuration file created.")


if __name__ == "__main__":
    create()