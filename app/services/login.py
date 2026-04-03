from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from app.config import WIFI_CONTROLLER, ADM_NAME, ADM_PWD

def login():
    options = webdriver.ChromeOptions()

    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--ignore-ssl-errors=yes')

    service = Service(executable_path="/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        login_url = WIFI_CONTROLLER
        driver.get(login_url)

        wait = WebDriverWait(driver, 10)

        adm_name_input = wait.until(EC.presence_of_element_located((By.NAME, "adm_name")))
        adm_name_input.send_keys(ADM_NAME)

        adm_pwd_input = driver.find_element(By.NAME, "adm_pwd")
        adm_pwd_input.send_keys(ADM_PWD)

        login_btn = driver.find_element(By.NAME, "Image6")
        login_btn.click()

        time.sleep(3)

        return driver

    except Exception as e:
        print(f"login failed: {e}")
        driver.quit()
        return None