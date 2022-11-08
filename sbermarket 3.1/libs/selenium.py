import time

from selenium import webdriver
from selenium.common import WebDriverException, exceptions
from selenium.webdriver.support import expected_conditions as EC

from config.conf import delay
from config.dev_conf import CHROMEDRIVER


def init_driver() -> webdriver.Chrome:
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-gpu-blacklist')
    options.add_argument('--use-gl')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent={}'.format(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'))
    options.add_experimental_option("excludeSwitches", ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ['enable-automation'])

    return driver


def safe_get(driver, url: str) -> bool:
    """ Goes to the page or else throws an error. """
    try:
        driver.get(url)
    except WebDriverException:
        return False

    return True


def does_element_exist(wait, locator) -> bool:
    """ Returns True if element exists or else False. """
    try:
        wait.until(
            EC.presence_of_element_located(
                locator
            )
        )
    except (exceptions.TimeoutException, exceptions.StaleElementReferenceException):
        return False

    return True


def scroll(driver) -> None:
    """
    Scrolls to the very bottom of the page, loads all the data, so later on we can get these elements
    and loop through them.

    :return:
    """
    if driver is None:
        raise TypeError('The driver has not been initialized.')

    pageHeight = driver.execute_script('return document.body.scrollHeight')

    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

        time.sleep(delay)

        bufferHeight = driver.execute_script('return document.body.scrollHeight')

        if bufferHeight == pageHeight:
            break

        pageHeight = bufferHeight
