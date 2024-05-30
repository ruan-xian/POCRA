from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import logging
import threading
import subprocess

__all__ = ["click_pokemon", "focus_window", "close_window"]

options = webdriver.ChromeOptions()
p = "https://ydarissep.github.io/PokeRogue-Pokedex"
options.add_argument(f"--app={p}")
options.add_experimental_option(
    "excludeSwitches", ["enable-logging", "enable-automation"]
)
options.add_experimental_option("useAutomationExtension", False)

svc = Service(ChromeDriverManager().install())
svc.HideCommandPromptWindow = True
svc.creation_flags = subprocess.CREATE_NO_WINDOW

browser = webdriver.Chrome(service=svc, options=options)


def focus_window():
    position = browser.get_window_position()
    browser.minimize_window()
    browser.set_window_position(position["x"], position["y"])


def close_window():
    browser.close()


# Wait for the pokedex to properly load


def wait_for_element(elem):
    while not elem.is_displayed() or not elem.is_enabled():
        time.sleep(0.1)


speciesButton = None
searchbar = None
initialized = False


def init_task():
    global speciesButton
    global searchbar
    global initialized
    while True:
        try:
            speciesButton = browser.find_element(By.ID, "speciesButton")
            wait_for_element(speciesButton)
            speciesButton.click()
            break
        except NoSuchElementException:
            time.sleep(0.5)
    searchbar = browser.find_element(By.ID, "speciesInput")
    initialized = True


t = threading.Thread(target=init_task)
t.start()

translation_dict = {ord(c): None for c in "♀♂:'."}
translation_dict.update({ord("é"): "e", ord("-"): " "})


def click_pokemon(name):
    while not initialized:
        time.sleep(0.5)

    cleaned_name = name.translate(translation_dict)

    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()

    wait_for_element(speciesButton)
    speciesButton.click()

    logging.info(f"Searching for {cleaned_name}")
    wait_for_element(searchbar)
    searchbar.clear()
    searchbar.send_keys(cleaned_name)

    processed_name = cleaned_name.upper().replace(" ", "_")
    logging.debug(f"Searching for {processed_name}")
    row = None

    MAX_TRIES = 20
    tries = 0
    while True:
        try:
            row = browser.find_element(By.ID, f"SPECIES_{processed_name}")
            break
        except NoSuchElementException:
            if tries >= MAX_TRIES:
                logging.error(f"Could not find {cleaned_name}")
                return
            tries += 1
            time.sleep(0.1)

    wait_for_element(row)
    row.click()


def main():
    while not initialized:
        time.sleep(0.5)
    click_pokemon("Patrat")
    time.sleep(5)
    click_pokemon("Venusaur Mega")
    input()


if __name__ == "__main__":
    main()
