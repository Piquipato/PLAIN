from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
import random
import click
import time
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


def waiting(t: int = 3, dt: int = 0.6):
    time.sleep(max(0, random.gauss(t, dt)))


@log_step
def ficha_start(
    email: str,
    passwd: str,
    headless: bool = True,
):
    logging.info("Starting FichaBot...")
    logging.info("Setting up Chrome WebDriver...")
    options = Options()
    options.add_argument("--headless") \
        if headless else None
    driver = webdriver.Chrome(
        options=options
    )
    logging.info("WebDriver started successfully.")

    web_url = "https://app.plain.ninja/login"
    logging.info(f"Navigating to login page: {web_url}...")
    driver.get(web_url)
    waiting()
    email_input = driver.find_element(
        By.XPATH,
        "//input[@type='email']"
    )
    waiting(1, 0.2)
    email_input.send_keys(email)
    passwd_input = driver.find_element(
        By.XPATH,
        "//input[@type='password']"
    )
    waiting(1, 0.2)
    passwd_input.send_keys(passwd)
    login_button = driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    )
    login_button.click()
    logging.info("Logged in successfully. Waiting...")
    waiting(5, 1)

    logging.info("Checking in for a hard day's work...")
    checkin_button = driver.find_element(
        By.XPATH,
        "//button[@type='button' and normalize-space(text())='Fichar entrada']"
    )
    checkin_button.click()
    logging.info("Checked in successfully! Exiting...")
    waiting(2, 0.4)
    driver.quit()


@log_step
def ficha_stop(
    email: str,
    passwd: str,
    headless: bool = True,
):
    logging.info("Ending FichaBot...")
    logging.info("Setting up Chrome WebDriver...")
    options = Options()
    options.add_argument("--headless") \
        if headless else None
    driver = webdriver.Chrome(
        options=options
    )
    logging.info("WebDriver started successfully.")

    web_url = "https://app.plain.ninja/login"
    logging.info(f"Navigating to login page: {web_url}...")
    driver.get(web_url)
    waiting()
    email_input = driver.find_element(
        By.XPATH,
        "//input[@type='email']"
    )
    waiting(1, 0.2)
    email_input.send_keys(email)
    passwd_input = driver.find_element(
        By.XPATH,
        "//input[@type='password']"
    )
    waiting(1, 0.2)
    passwd_input.send_keys(passwd)
    login_button = driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    )
    login_button.click()
    logging.info("Logged in successfully. Waiting...")
    waiting(5, 1)

    logging.info("Checking out for a hard day's work...")
    checkin_button = driver.find_element(
        By.XPATH,
        "//button[@type='button' and normalize-space(text())='Detener']"
    )
    checkin_button.click()
    logging.info("Checked out successfully! Exiting...")
    waiting(2, 0.4)
    driver.quit()


def _fichabot(
    log_file: str = os.path.join(
        HOME_DIR,
        "logs",
        "fichabot_{timestamp}.log".format(
            timestamp=time.strftime("%Y%m%d%H%M%S")
        ),
    ),
    log_level: str = "INFO",
):
    setup_logging(
        log_file=log_file,
        log_level=LOG_LEVELS.get(log_level, logging.INFO),
    )
    logging.info("Started FichaBot daemon process, waiting for scheduled tasks...")


def cli(*args):
    import argparse
    parser = argparse.ArgumentParser(
        description="FichaBot CLI - A command line interface for FichaBot."
    )

    cliargs = parser.parse_args(*args)


if __name__ == "__main__":
    cli()