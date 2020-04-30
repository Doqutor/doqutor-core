

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import secrets
from time import sleep

LOGIN_URL = "https://www.google.com"
driver = webdriver.Firefox()
driver.get(LOGIN_URL)

for i in range(15):
    driver.implicitly_wait(3)
    driver.find_element_by_name("q").send_keys("dfsdfkljsdflsfd")
