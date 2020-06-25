import os
from datetime import time

from django.test import TestCase
from dotenv import load_dotenv
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

EMAIL = os.getenv('LOGIN_EMAIL')
PASSWORD = os.getenv('LOGIN_PASSWORD')

class TestLogin():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_untitled(self):
        # Test name: Untitled
        load_dotenv()
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get("")     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 4 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 5 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get("")     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        '''# 11 | assertConfirmation | Are you sure? |
        assert self.driver.switch_to.alert.text == "Are you sure?"
        # 12 | webdriverChooseCancelOnVisibleConfirmation |  |
        self.driver.switch_to.alert.dismiss()
        # 13 | click | css=.fa-envelope |
        self.driver.find_element(By.CSS_SELECTOR, ".fa-envelope").click()'''
