from xmlrpc.client import boolean
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import webelement
from selenium import webdriver
import uuid
import os
import shutil

MAX_WAIT = 10

class WebDriverWrapper:

    def __init__(self):
        self.driver = self.__get_driver()
        self.wait = WebDriverWait(self.driver, MAX_WAIT)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            print(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()
        shutil.rmtree(self._tmp_folder)

        return True
    
    def __get_driver(self):
        self._tmp_folder = '/tmp/{}'.format(uuid.uuid4())
        if not os.path.exists(self._tmp_folder):
            os.makedirs(self._tmp_folder)

        if not os.path.exists(self._tmp_folder + '/chrome-user-data'):
            os.makedirs(self._tmp_folder + '/chrome-user-data')

        if not os.path.exists(self._tmp_folder + '/data-path'):
            os.makedirs(self._tmp_folder + '/data-path')

        if not os.path.exists(self._tmp_folder + '/cache-dir'):
            os.makedirs(self._tmp_folder + '/cache-dir')

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = "/opt/chrome/chrome"
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("window-size=2560x1440")
        chrome_options.add_argument(f"--user-data-dir={self._tmp_folder}/chrome-user-data")
        chrome_options.add_argument(f"--data-path={self._tmp_folder}/data-path")
        chrome_options.add_argument(f"--disk-cache-dir={self._tmp_folder}/cache-dir")
        chrome_options.add_argument("--remote-debugging-port=9222")
        input_driver = webdriver.Chrome("/opt/chromedriver", options=chrome_options)
        return input_driver
