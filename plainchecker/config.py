try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
    from plainchecker.create import (
        parse_schedule,
        parse_work_days,
        parse_exceptions,
    )
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
    from create import (
        parse_schedule,
        parse_work_days,
        parse_exceptions,
    )
import datetime
import click
import json
import os

@click.command(
    help="Update user configuration for PlainChecker.",
    name="config",
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
def config(
    username: str,
    email: str,
    work_days: str = "",
    exceptions: str = "",
    schedule: str = "",
    log_level: str = "INFO",
):
    logger = setup_logging(
        log_level=log_level,
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_config_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
    )
    logger.info(f"Updating configuration for user {username} with email {email}...")
    config_file = os.path.join(CONFIG_DIR, f"{username}.json")
    config_json = json.load(open(config_file, "r"))
    user_config = next((i for i, conf in enumerate(config_json) \
                        if conf.get("email") == email), None)
    if user_config is None:
        raise ValueError(f"Email {email} not found in the configuration for user {username}.")
    old_config = config_json[user_config]
    exceptions_lst = [
        date for exc in exceptions for date in parse_exceptions(exc)
    ]
    work_days_lst = [
        day for wd in work_days for day in parse_work_days(wd)
    ]
    new_config = dict(
        username=username,
        email=email,
        work_days=work_days_lst if work_days_lst else [1, 2, 3, 4, 5],
        exceptions=exceptions_lst if exceptions_lst else [],
        schedule=parse_schedule(schedule) if schedule else ["09:00", "17:00"],
    )
    config_json[user_config] = new_config
    with open(config_file, "w") as f:
        json.dump(config_json, f, indent=4)
    logger.info(f"Configuration for user {username} updated successfully.")


if __name__ == "__main__":
    config()