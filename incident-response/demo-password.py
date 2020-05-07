

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import secrets
from time import sleep

username = input("What username? ")

LOGIN_URL = "https://login-doqutore-infrastructure-prod.auth.ap-southeast-2.amazoncognito.com/login?client_id=1l26brptvhg0hhricpnno0h45d&response_type=token&scope=doqutore/application&redirect_uri=https://prod.aws9447.me/login"
driver = webdriver.Firefox()
driver.get(LOGIN_URL)

for i in range(15):
    driver.implicitly_wait(3)
    sleep(1)
    driver.execute_script(f'document.getElementsByName("username")[1].value="{username}"')
    driver.execute_script(f'document.getElementsByName("password")[1].value="{secrets.token_urlsafe(8)}"')
    sleep(1)
    driver.execute_script(f'document.getElementsByName("cognitoSignInForm")[1].submit()')
