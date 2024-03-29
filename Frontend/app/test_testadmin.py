# Generated by Selenium IDE
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from django.test import TestCase

EMAIL = os.getenv('T_USER2')
PASSWORD = os.getenv('T_PW2')

class TestTestadmin():
  def setUp(self) -> None:
    self.driver = webdriver.Chrome(ChromeDriverManager().install())
    self.vars = {}
  
  def tearDown(self) -> None:
    self.driver.quit()
  
  def test_testadmin(self):
    load_dotenv()
    # Test name: test_admin
    # Step # | name | target | value
    # 1 | open | /login/ | 
    self.driver.get("http://localhost:8000/login/")
    # 2 | setWindowSize | 1440x900 | 
    self.driver.set_window_size(1440, 900)
    # 3 | click | id=id_username | 
    self.driver.find_element(By.ID, "id_username").click()
    # 4 | type | id=id_username | luismiguel
    self.driver.find_element(By.ID, "id_username").send_keys(EMAIL)
    # 5 | click | id=id_password | 
    self.driver.find_element(By.ID, "id_password").click()
    # 6 | type | id=id_password | luis1234
    self.driver.find_element(By.ID, "id_password").send_keys(PASSWORD)
    # 7 | click | css=.btn | 
    self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
    # 8 | click | css=.row | 
    self.driver.find_element(By.CSS_SELECTOR, ".row").click()
    # 9 | click | css=.grid-item:nth-child(5) .rounded | 
    self.driver.find_element(By.CSS_SELECTOR, ".grid-item:nth-child(5) .rounded").click()
    # 10 | click | linkText=Create Iperf Server | 
    self.driver.find_element(By.LINK_TEXT, "Create Iperf Server").click()
    # 11 | click | id=ip | 
    self.driver.find_element(By.ID, "ip").click()
    # 12 | type | id=ip | 192.168.0.1
    self.driver.find_element(By.ID, "ip").send_keys("192.168.0.1")
    # 13 | click | css=form:nth-child(4) | 
    self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(4)").click()
    # 14 | click | id=port | 
    self.driver.find_element(By.ID, "port").click()
    # 15 | type | id=port | 5000
    self.driver.find_element(By.ID, "port").send_keys("5000")
    # 16 | click | css=.btn | 
    self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
    # 17 | click | linkText=AMazING | 
    self.driver.find_element(By.LINK_TEXT, "AMazING").click()
    # 18 | click | linkText=Reservations | 
    self.driver.find_element(By.LINK_TEXT, "Reservations").click()
    # 19 | click | css=.month:nth-child(4) | 
    self.driver.find_element(By.CSS_SELECTOR, ".month:nth-child(4)").click()
    # 20 | click | css=.calendar-body:nth-child(7) > .calendar-day:nth-child(4) > .day | 
    self.driver.find_element(By.CSS_SELECTOR, ".calendar-body:nth-child(7) > .calendar-day:nth-child(4) > .day").click()
    # 21 | click | linkText=Register Test | 
    self.driver.find_element(By.LINK_TEXT, "Register Test").click()
    # 22 | click | id=name | 
    self.driver.find_element(By.ID, "name").click()
    # 23 | type | id=name | Teste
    self.driver.find_element(By.ID, "name").send_keys("Teste")
    # 24 | click | id=begin_date | 
    self.driver.find_element(By.ID, "begin_date").click()
    # 25 | type | id=begin_date | 05/02/2020 12:31
    self.driver.find_element(By.ID, "begin_date").send_keys("05/02/2020 12:31")
    # 26 | click | id=end_date | 
    self.driver.find_element(By.ID, "end_date").click()
    # 27 | type | id=end_date | 05/02/2020 14:50
    self.driver.find_element(By.ID, "end_date").send_keys("05/02/2020 14:50")
    # 28 | click | css=.btn | 
    self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
    # 29 | click | linkText=AMazING | 
    self.driver.find_element(By.LINK_TEXT, "AMazING").click()
    # 30 | click | linkText=Reservations | 
    self.driver.find_element(By.LINK_TEXT, "Reservations").click()
    # 31 | click | linkText=Statistics | 
    self.driver.find_element(By.LINK_TEXT, "Statistics").click()
    # 32 | click | linkText=Users | 
    self.driver.find_element(By.LINK_TEXT, "Users").click()
    # 33 | click | linkText=Previous Experiences | 
    self.driver.find_element(By.LINK_TEXT, "Previous Experiences").click()
    # 34 | click | css=tr:nth-child(1) .btn | 
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn").click()
    # 35 | click | linkText=AMazING | 
    self.driver.find_element(By.LINK_TEXT, "AMazING").click()
    # 36 | click | id=navbarDropdown | 
    self.driver.find_element(By.ID, "navbarDropdown").click()
    # 37 | click | linkText=Logout | 
    self.driver.find_element(By.LINK_TEXT, "Logout").click()
  
