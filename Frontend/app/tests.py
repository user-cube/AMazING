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

site = ""
cmd_exec = ''
class TestLogin():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 8 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()

class TestNetworkStatus():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | linkText=APU 3 |
        self.driver.find_element(By.LINK_TEXT, "APU 3").click()
        # 8 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 9 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 10 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()


class TestNodeStatus():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | linkText=APU 3 |
        self.driver.find_element(By.LINK_TEXT, "APU 3").click()
        # 7 | click | linkText=Create Iperf Server |
        self.driver.find_element(By.LINK_TEXT, "Create Iperf Server").click()
        # 8 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 9 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 10 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()


class TestCreateIperfServer():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)  # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | linkText=APU 3 |
        self.driver.find_element(By.LINK_TEXT, "APU 3").click()
        # 8 | click | linkText=Create Iperf Server |
        self.driver.find_element(By.LINK_TEXT, "Create Iperf Server").click()
        # 9 | type | id=id_password | 1234
        self.driver.find_element(By.ID, "ip").click()
        # 10 | type | id=id_password | 1234
        self.driver.find_element(By.ID, "ip").send_keys("192.168.0.1")
        # 11 | type | id=id_password | 1234
        self.driver.find_element(By.ID, "port").click()
        # 12 | type | id=id_password | 1234
        self.driver.find_element(By.ID, "port").send_keys("5000")
        # 13 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 14 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 15 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 16 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 17 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()


class TestCreateIperfClient():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)  # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | linkText=APU 3 |
        self.driver.find_element(By.LINK_TEXT, "APU 3").click()
        # 8 | click | linkText=Create Iperf Server |
        self.driver.find_element(By.LINK_TEXT, "Create Iperf Client").click()
        # 9 | type | id=ip | 1234
        self.driver.find_element(By.ID, "ip").click()
        # 10 | type | id=ip | 1234
        self.driver.find_element(By.ID, "ip").send_keys("192.168.0.1")
        # 11 | type | id=port | 1234
        self.driver.find_element(By.ID, "port").click()
        # 12 | type | id=port | 1234
        self.driver.find_element(By.ID, "port").send_keys("5000")
        # 13 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 14 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 15 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 16 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()


class TestCalendar():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | linkText=Reservations |
        self.driver.find_element(By.LINK_TEXT, "Reservations").click()
        # 8 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 9 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 10 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()


class TestRegisterTestCalendar():
    def setUp(self) -> None:
        # mudar link
        self.driver = webdriver.Remote(
            command_executor=cmd_exec, desired_capabilities=DesiredCapabilities.CHROME)
        self.vars = {}

    def tearDown(self) -> None:
        self.driver.quit()

    def test_loginTest(self):
        load_dotenv()
        # Test name: LoginTest
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get(site)     # place the website link
        # 2 | setWindowSize | 1552x849 |
        self.driver.set_window_size(1552, 849)
        # 3 | click | linkText=Log in |30'
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        # 4 | type | id=id_username | EMAIL
        self.driver.find_element(By.ID, "id_username").send_keys(
            EMAIL)
        # 5 | type | id=id_password | PASSWORD
        self.driver.find_element(By.ID, "id_password").send_keys(
            PASSWORD)
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 7 | click | linkText=APU 3 |
        self.driver.find_element(By.LINK_TEXT, "Reservations").click()
        # 6 | click | css=.btn |
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        # 9 | type | id=ip | 1234
        self.driver.find_element(By.ID, "name").click()
        # 10 | type | id=ip | 1234
        self.driver.find_element(By.ID, "name").send_keys("My Experiment")
        # 9 | type | id=ip | 1234
        self.driver.find_element(By.ID, "begin_date").click()
        # 10 | type | id=ip | 1234
        self.driver.find_element(By.ID, "begin_date").send_keys("05/16/2018 12:31")
        # 9 | type | id=ip | 1234
        self.driver.find_element(By.ID, "end_date").click()
        # 10 | type | id=ip | 1234
        self.driver.find_element(By.ID, "end_date").send_keys("05/16/2018 12:35")
        # 8 | click | id=navbarDefault |
        self.driver.find_element(By.ID, "navbarDefault").click()
        # 9 | click | id=navbarDropdown |
        self.driver.find_element(By.ID, "navbarDropdown").click()
        # 10 | click | linkText=Logout |
        self.driver.find_element(By.LINK_TEXT, "Logout").click()