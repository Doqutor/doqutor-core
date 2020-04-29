

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import secrets
from time import sleep

LOGIN_URL = "https://login-doqutore-infrastructure-prod.auth.ap-southeast-2.amazoncognito.com/login?client_id=1l26brptvhg0hhricpnno0h45d&response_type=token&scope=doqutore/application&redirect_uri=https://prod.aws9447.me/login"
driver = webdriver.Firefox()
driver.get(LOGIN_URL)

for i in range(15):
    driver.implicitly_wait(10)
    driver.find_element_by_name('username').send_keys('tom')
    driver.find_element_by_name("cognitoSignInForm").submit()

    
