try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
    from plainchecker.server import send_command
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
    from server import send_command
from datetime import datetime
import tabulate
import socket
import pickle
import psutil
import click
import os


def check_servers(timeout: float = 0.5) -> list:
    available_servers = []
    conns = [
        conn for conn in psutil.net_connections(kind='inet')
        if conn.type == socket.SOCK_STREAM and \
        conn.family == socket.AF_INET and \
        conn.status == 'LISTEN'
    ]
    for conn in conns:
        try:
            response = send_command(
                "ping",
                host=conn.laddr.ip,
                port=conn.laddr.port,
                timeout=timeout
            )
            if response == "pong":
                available_servers.append({
                    "pid": conn.pid,
                    "ip": conn.laddr.ip,
                    "port": conn.laddr.port
                })
        except Exception as e:
            # Ignore any errors in sending the ping command
            continue
    return available_servers


@click.command(
    help="List all available PlainChecker servers.",
    name="lsserv",
)
@click.option(
    "--timeout", "-t",
    type=float,
    default=0.5,
    help="Timeout for the server response in seconds. Default is 0.5 seconds."
)
def lsserv(timeout: float = 0.5):
    logger = setup_logging(
        log_level="INFO",
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_lsserv_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
    )
    logger.info("Listing available PlainChecker servers...")
    
    servers = check_servers(timeout=timeout)
    if not servers:
        logger.info("No PlainChecker servers are currently running.")
    else:
        table = tabulate.tabulate(
            [
                [server["pid"], server["ip"], server["port"]]
                for server in servers
            ],
            headers=["PID", "IP Address", "Port"],
            tablefmt="grid"
        )
        logger.info("Available PlainChecker servers:\n" + table)

if __name__ == "__main__":
    lsserv()