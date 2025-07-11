from datetime import datetime, timedelta
import typing as tp
import keyring
import logging
import getpass
import click
import time
import json
import os

try:
    from fichabot.logger import (
        log_step,
        setup_logging,
        LOG_LEVELS
    )
except ImportError:
    from logger import (
        log_step,
        setup_logging,
        LOG_LEVELS
    )


HOME_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
HOME_DIR = os.environ.get("FICHABOT_HOME", HOME_DIR)

def parse_dates(date_str: str):
    date_lst = date_str.split(",")
    out = []
    for date_l in date_lst:
        if "-" in date_l and "/" in date_l:
            start_str, end_str = date_l.split('-')
            start_date = datetime.strptime(start_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_str, "%d/%m/%Y")
            out += [
                start_date + timedelta(days=i)
                for i in range((end_date - start_date).days + 1)
            ]
        if "-" in date_l and not "/" in date_l:
            min_str, max_str = date_l.split('-')
            min_num = int(min_str)
            max_num = int(max_str)
            out += list(range(min_num, max_num + 1))
        if "/" in date_l and not "-" in date_l:
            date_obj = datetime.strptime(date_l, "%d/%m/%Y")
            out += [date_obj]
        if date_l.isdigit() and not "-" in date_l and not "/" in date_l:
            out += [int(date_l)]
    return out


def create_user_config(
    username: str,
    email: str = None,
    passwd: str = None,
    exceptions: str = None,
    timetable: str = None,
):
    logging.info(f"Creating user configuration for {username}...")
    config_json = os.path.join(
        HOME_DIR, "config", f"{username}.json"
    )
    if not email:
        email = input("Enter your email: ")
    if not passwd:
        setup = False
        while not setup:
            passwd = getpass.getpass("Enter your password: ")
            repasswd = getpass.getpass("Repeat your password: ")
            if passwd != repasswd:
                logging.warning("Passwords do not match!")
            else:
                setup = True
    keyring.set_password(
        "fichabot",
        email,
        passwd
    )
    if not exceptions:
        exceptions = input(
            "Enter holidays (dd/mm/yyyy): "
        )
    exceptions = parse_dates(exceptions)
    if any(not isinstance(d, datetime) for d in exceptions):
        raise ValueError(
            "Invalid date format in exceptions. " \
            "Dates must be entered as dd/mm/yyyy. " \
            "Ranges of dates can be entered by adding a '-'."
        )
    if not timetable:
        timetable = input(
            "Enter timetable: "
        )
    timetable = parse_dates(timetable)
    if any(not isinstance(d, int) for d in timetable) or \
        any(d > 7 or d < 1 for d in timetable):
        raise ValueError(
            "Invalid weekday format, must be an integer or a " \
            "range of them, using '-', between 1 and 7"
        )
    user_config = dict(
        username=username,
        email=email,
        exceptions=[d.strftime("%d/%m/%Y") for d in exceptions],
        timetable=timetable,
    )
    with open(config_json, "w") as f:
        json.dump(user_config, f, indent=4)
    logging.info(
        f"User configuration for {username} created successfully."
    )


def _config(
    username: str = None,
    email: str = None,
    passwd: str = None,
    exceptions: str = None,
    timetable: str = None,
    display: bool = True,
    log_file: str = os.path.join(
        HOME_DIR,
        "logs",
        "fichabot_config_{timestamp}.log".format(
            timestamp=time.strftime("%Y%m%d%H%M%S")
        ),
    ),
    log_level: str = "INFO",
):
    setup_logging(
        log_file=log_file,
        log_level=LOG_LEVELS.get(log_level, logging.INFO),
    )
    logging.info("Configuring FichaBot...")
    if not username:
        username = input("Enter your username: ")
    config_json = os.path.join(
        HOME_DIR, "config", f"{username}.json"
    )
    if not os.path.exists(config_json) or \
        not os.path.isfile(config_json):
        logging.warning(f"User {username} not found!")
        logging.warning("Creating new user configuration...")
        create_user_config(
            username=username,
            email=email,
            passwd=passwd,
            exceptions=exceptions,
            timetable=timetable,
        )
    else:
        with open(config_json, "r") as f:
            user_config = json.load(f)
        logging.info(f"User configuration for {username} loaded successfully.")
        logging.info(f"Email: {user_config['email']}")
        if exceptions:
            exceptions = parse_dates(exceptions)
            exception_str = ', '.join(map(lambda x: datetime.strftime(x, "%d/%m/%Y"), exceptions))
            logging.info(
                f"New exceptions: {exception_str}"
            )
            if any(not isinstance(d, datetime) for d in exceptions):
                raise ValueError(
                    "Invalid date format in exceptions. " \
                    "Dates must be entered as dd/mm/yyyy. " \
                    "Ranges of dates can be entered by adding a '-'."
                )
            user_config['exceptions'] = [
                d.strftime("%d/%m/%Y") for d in exceptions
            ]
        if timetable:
            timetable = parse_dates(timetable)
            logging.info(
                f"New timetable: {', '.join(map(str, timetable))}"
            )
            if any(not isinstance(d, int) for d in timetable) or \
                any(d > 7 or d < 1 for d in timetable):
                raise ValueError(
                    "Invalid weekday format, must be an integer or a " \
                    "range of them, using '-', between 1 and 7"
                )
            user_config['timetable'] = timetable
        with open(config_json, "w") as f:
            json.dump(user_config, f, indent=4)
    if display:
        with open(config_json, "r") as f:
            user_config = json.load(f)
            logging.info(
                f"\n{json.dumps(user_config, indent=4)}"
            )
    logging.info("User configuration updated successfully.")


def cli(*args):
    import argparse
    parser = argparse.ArgumentParser(
        description="Configure FichaBot user settings."
    )
    parser.add_argument(
        "--username",
        "-u",
        type=str,
        required=True,
        help="Username for the FichaBot user.",
    )
    parser.add_argument(
        "--email",
        "-e",
        type=str,
        help="Email address for the FichaBot user.",
        default="",
    )
    parser.add_argument(
        "--passwd",
        "-p",
        type=str,
        help="Password for the FichaBot user. If not provided, you will be prompted to enter it.",
        default="",
    )
    parser.add_argument(
        "--exceptions",
        "-x",
        type=str,
        help="Holidays or exceptions in dd/mm/yyyy format, separated by commas. " \
             "Ranges of dates can be entered by adding a '-'.",
        default="",
    )
    parser.add_argument(
        "--timetable",
        "-t",
        type=str,
        help="Week days in integer format, separated by commas. " \
             "Ranges of dates can be entered by adding a '-'. " \
             "1 for Monday, 2 for Tuesday, ..., 7 for Sunday.",
        default="",
    )
    parser.add_argument(
        "--display/--no-display",
        "-d/-nd",
        dest="display",
        default=True,
        help="Display the user configuration after updating it. " \
             "If --no-display is set, the configuration will not be displayed.",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        choices=list(LOG_LEVELS.keys()),
        default="INFO",
        help="Logging level for the FichaBot configuration.",
    )
    cliargs = parser.parse_args(*args)
    _config(
        username=cliargs.username,
        email=cliargs.email,
        passwd=cliargs.passwd,
        exceptions=cliargs.exceptions,
        timetable=cliargs.timetable,
        display=cliargs.display,
        log_level=cliargs.log_level,
    )


if __name__ == "__main__":
    cli()