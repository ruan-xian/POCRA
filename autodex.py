from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import logging
from os import path
import threading

__all__ = ["click_pokemon", "focus_window", "close_window"]

options = webdriver.ChromeOptions()
p = path.abspath(path.join(path.dirname(__file__), "PokeRogue-Pokedex/index.html"))
options.add_argument(f"--app={p}")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--log-level=3")

svc = Service(ChromeDriverManager().install())
svc.HideCommandPromptWindow = True

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


def click_pokemon(name):
    while not initialized:
        time.sleep(0.5)

    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()

    wait_for_element(speciesButton)
    speciesButton.click()

    logging.info(f"Searching for {name}")
    wait_for_element(searchbar)
    searchbar.clear()
    searchbar.send_keys(name)

    processed_name = name.upper().replace(" ", "_")
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
                logging.error(f"Could not find {name}")
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
