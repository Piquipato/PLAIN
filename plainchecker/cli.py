try:
    from plainchecker.config import config
    from plainchecker.create import create
    from plainchecker.remove import remove
    from plainchecker.lsserv import lsserv
    from plainchecker.send import send
    from plainchecker.start import start
    from plainchecker.stop import stop
except ModuleNotFoundError:
    from config import config
    from create import create
    from remove import remove
    from lsserv import lsserv
    from send import send
    from start import start
    from stop import stop
import click


@click.group(
    name="plainchecker",
    help="Plainchecker command to control check-in bot."
)
def plainchecker():
    pass

for command in [
    config,
    create,
    remove,
    lsserv,
    send,
    start,
    stop
]:
    plainchecker.add_command(
        command, command.name,
    )


if __name__ == '__main__':
    plainchecker()
