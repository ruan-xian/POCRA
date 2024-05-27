from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import logging
import os

__all__ = ["click_pokemon"]

options = webdriver.ChromeOptions()
p = os.path.abspath(r"./PokeRogue-Pokedex/index.html")
options.add_argument(f"--app={p}")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--log-level=3")

browser = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

# Wait for the pokedex to properly load


def wait_for_element(elem):
    while not elem.is_displayed() or not elem.is_enabled():
        time.sleep(0.1)


speciesButton = None
while True:
    try:
        speciesButton = browser.find_element(By.ID, "speciesButton")
        wait_for_element(speciesButton)
        speciesButton.click()
        break
    except NoSuchElementException:
        time.sleep(0.5)
searchbar = browser.find_element(By.ID, "speciesInput")


def click_pokemon(name):
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
    while True:
        try:
            row = browser.find_element(By.ID, f"SPECIES_{processed_name}")
            break
        except NoSuchElementException:
            time.sleep(0.1)

    wait_for_element(row)
    row.click()


def main():
    click_pokemon("Patrat")
    time.sleep(5)
    click_pokemon("Venusaur Mega")
    input()


if __name__ == "__main__":
    main()
