try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
from datetime import datetime
import keyring
import click
import json
import os


@click.command(
    help="Remove a user configuration from PlainChecker.",
    name="remove",
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
    "--log-level", "-l",
    type=click.Choice(list(LOG_LEVELS.keys()), case_sensitive=False),
    default="INFO",
    help="Logging level for the user configuration. Default is INFO."
)
def remove(
    username: str,
    email: str,
    log_level: str = "INFO",  
):
    logger = setup_logging(
        log_level=log_level,
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_remove_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
    )
    logger.info(f"Removing email {email} from username {username}...")
    config_file = os.path.join(CONFIG_DIR, f"{username}.json")
    if not os.path.exists(config_file):
        raise ValueError(f"Configuration for user {username} does not exist.")
    config_json: list = json.load(open(config_file, "r"))
    user_config = next((i for i, conf in enumerate(config_json) \
                        if conf.get("email") == email), None)
    if user_config is None:
        raise ValueError(f"Email {email} not found in the configuration for user {username}.")
    config_json = config_json[:user_config] + config_json[user_config + 1:]
    with open(config_file, "w") as f:
        json.dump(config_json, f, indent=4)
    keyring.delete_password(
        f"plainchecker_{username}",
        email
    )
    logger.info(f"Email {email} from username {username} removed successfully.")


if __name__ == "__main__":
    remove()