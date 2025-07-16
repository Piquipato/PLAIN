try:
    from plainchecker import CONFIG_DIR, LOG_DIR
    from plainchecker.logger import setup_logging, LOG_LEVELS
except ModuleNotFoundError:
    from __init__ import CONFIG_DIR, LOG_DIR
    from logger import setup_logging, LOG_LEVELS
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import (
    datetime,
    timedelta,
)
import typing as tp
import pandas as pd
import numpy as np
import traceback
import keyring
import logging
import random
import click
import time
import json
import os


def wait(t: int = 3, dt: int = 0.6):
    time.sleep(max(0, random.gauss(t, dt)))


def check_in(
    username: str,
    email: str,
    times: tp.Tuple[str, str],
    headless: bool = True,
):
    logging.info("Starting check-in process...")
    logging.info("Configuring Selenium WebDriver...")
    options = Options()
    options.add_argument("--headless") \
        if headless else None
    driver = webdriver.Chrome(
        options=options
    )

    logging.info("Getting webpage and logging in...")
    web_url = "https://app.plain.ninja/login"
    driver.get(web_url)
    wait()
    email_input = driver.find_element(
        By.XPATH,
        "//input[@type='email']"
    )
    wait(1, 0.2)
    email_input.send_keys(email)
    passwd_input = driver.find_element(
        By.XPATH,
        "//input[@type='password']"
    )
    wait(1, 0.2)
    passwd = keyring.get_password(
        f"plainchecker_{username}",
        email
    )
    passwd_input.send_keys(passwd)
    login_button = driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    )
    login_button.click()
    logging.info("Logged in successfully!")
    wait()

    logging.info("Navigating to check-in page...")
    checkin_page = driver.find_element(
        By.XPATH,
        "//a[@href='/my-times']"
    )
    checkin_page.click()
    wait()

    logging.info("Filling in check-in times...")
    start_time = driver.find_element(
        By.XPATH,
        "//tr[contains(@class, 'today')]/td/form/span/input[@type='time' and contains(@id, 'start')]"
    )
    end_time = driver.find_element(
        By.XPATH,
        "//tr[contains(@class, 'today')]/td/form/span/input[@type='time' and contains(@id, 'end')]"
    )
    driver.execute_script("""
        var input = arguments[0];
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(input, arguments[1]);
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
    """, start_time, times[0])
    wait(2, 0.4)
    driver.execute_script("""
        var input = arguments[0];
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(input, arguments[1]);
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
    """, end_time, times[1])
    wait(5, 0.2)
    logging.info("All Done!")


KEYS = {
    "username": str,
    "email": str,
    "work_days": tp.List[int],
    "exceptions": tp.List[str],
    "schedule": tp.Tuple[str, str],
}

def check_json(data: tp.Dict[str, tp.Any]) -> bool:
    return all(
        key in KEYS and (
            isinstance(val, str) if KEYS[key] is str
            else isinstance(val, list) and all(isinstance(x, str) for x in val) if KEYS[key] is tp.List[str]
            else isinstance(val, list) and all(isinstance(x, int) for x in val) if KEYS[key] is tp.List[int]
            else (isinstance(val, tuple) or isinstance(val, list)) and len(val) == 2 and all(isinstance(x, str) for x in val)
        )
        for key, val in data.items()
    )


def randomize_schedule(
    schedule: tp.Tuple[str, str],
    extra_time_mean: float = 5, # mins
    extra_time_std: float = 1, # mins
) -> tp.Tuple[str, str]:
    extra_mins = np.random.gamma(
        shape = (extra_time_mean / extra_time_std) ** 2,
        scale = extra_time_std ** 2 / extra_time_mean,
        size = 2
    )
    (start, end) = (datetime.strptime(entry, "%H:%M") for entry in schedule)
    start -= timedelta(minutes=extra_mins[0])
    end += timedelta(minutes=extra_mins[1])
    return (
        start.strftime("%H:%M"),
        end.strftime("%H:%M")
    )


def check(
    extra_time_mean: float = 5,  # mins
    extra_time_std: float = 1,  # mins
):
    logger = setup_logging(
        log_cmd=True,
        log_level=10,
        log_file=os.path.join(
            LOG_DIR,
            f"plainchecker_check_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
    )
    logging.info("Grabbing configuration files...")
    configs = [
        file for file in os.listdir(CONFIG_DIR)
        if file.endswith(".json")
    ]
    jsons = pd.DataFrame([
        el for file in configs
        for el in json.load(open(os.path.join(CONFIG_DIR, file), "r"))
        if isinstance(el, dict) and check_json(el)
    ])
    logging.info(f"Found {len(jsons.index)} valid configurations.")

    logging.info("Starting check-in process for each configuration...")
    today = datetime.now().strftime("%d/%m/%Y")
    work_day = datetime.now().weekday() + 1
    for i in range(len(jsons.index)):
        config = jsons.iloc[i, :].to_dict()
        username = config["username"]
        if today in config["exceptions"]:
            logging.warning(f"Skipping check-in for {username} on {today} due to exception.")
            continue
        if work_day not in config["work_days"]:
            logging.warning(f"Skipping check-in for {username} on {today} as it is not a work day.")
            continue
        try:
            schedule = randomize_schedule(
                config["schedule"],
                extra_time_mean=extra_time_mean,
                extra_time_std=extra_time_std
            )
            logging.info(f"Checking in for {username} with schedule {schedule}...")
            check_in(
                username=username,
                email=config["email"],
                times=schedule,
                headless=True
            )
        except Exception as e:
            logging.error(f"Error during check-in for {username}: {e}")
            logging.error(traceback.format_exc())
            continue
    logging.info("Check-in process completed for all configurations.")

