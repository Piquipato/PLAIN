try:
    from fichabot.config import _config
    from fichabot.logger import LOG_LEVELS
    from fichabot.fichabot import _fichabot
except ImportError:
    from config import _config
    from logger import LOG_LEVELS
    from fichabot import _fichabot
import click


@click.group(
    help="FichaBot CLI - A command line interface for FichaBot."
)
@click.pass_context
def fichabot(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Hola")


@click.command(
    help="Configure FichaBot user settings."
)
@click.option(
    "--username",
    "-u",
    type=str,
    required=True,
    help="Username for the FichaBot user.",
)
@click.option(
    "--email",
    "-e",
    type=str,
    help="Email address for the FichaBot user.",
    default="",
)
@click.option(
    "--passwd",
    "-p",
    type=str,
    help="Password for the FichaBot user. If not provided, you will be prompted to enter it.",
    default="",
)
@click.option(
    "--exceptions",
    "-x",
    type=str,
    help="Holidays or exceptions in dd/mm/yyyy format, separated by commas. " \
         "Ranges of dates can be entered by adding a '-'.",
    default="",
)
@click.option(
    "--timetable",
    "-t",
    type=str,
    help="Week days in integer format, separated by commas. " \
         "Ranges of dates can be entered by adding a '-'. " \
         "1 for Monday, 2 for Tuesday, ..., 7 for Sunday.",
    default="",
)
@click.option(
    "--display/--no-display",
    "-d/-nd",
    default=True,
    help="Display the user configuration after updating it. " \
        "If --no-display is set, the configuration will not be displayed.",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(LOG_LEVELS.keys(), case_sensitive=False),
    default="INFO",
    help="Logging level for the FichaBot configuration.",
)
def config(
    username: str = None,
    email: str = None,
    passwd: str = None,
    exceptions: str = None,
    timetable: str = None,
    display: bool = True,
    log_level: str = "INFO",
):
    _config(
        username=username,
        email=email,
        passwd=passwd,
        exceptions=exceptions,
        timetable=timetable,
        display=display,
        log_level=log_level,
    )


fichabot.add_command(config, name="config")

if __name__ == "__main__":
    fichabot()