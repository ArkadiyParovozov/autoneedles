"""
restarts codeanywhere containers
"""

import argparse
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def restart(email, password):
    """
    restarts codeanywhere container

    :param email: codeanywhere login
    :param password: codeanywhere password

    """
    service = ChromeService(executable_path=ChromeDriverManager().install())

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://dashboard.codeanywhere.com/')

    driver.find_element(By.NAME, 'login_email').send_keys(email)
    driver.find_element(By.NAME, 'login_password').send_keys(password)
    driver.find_element(By.NAME, 'login_remember').is_selected()
    driver.find_element(By.XPATH, '//input[@value="Login"]').submit()
    WebDriverWait(driver, timeout=10).until(
        lambda x: x.find_element(By.XPATH, '//div[@class="card-options tab-focus"]')
    ).click()
    driver.find_element(
        By.XPATH,
        '//div[@class="options-menu__item tab-focus" and contains(text(),"Restart")]'
    ).click()

    time.sleep(15)

    driver.quit()


def main():
    """
    restarts codeanywhere container

    """
    parser = argparse.ArgumentParser(
        description='restarts codeanywhere container',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--email', type=str, help='codeanywhere login')
    parser.add_argument('--password', type=str, default=4, help='codeanywhere password')
    args = parser.parse_args()

    restart(args.email, args.password)


if __name__ == '__main__':
    main()
