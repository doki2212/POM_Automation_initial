import os
import time
from datetime import datetime
from pom.core.base_page import BasePage

USERNAME_XPATH = "//*[@id='login-form_username']"
PASSWORD_XPATH = "//*[@id='login-form_password']"
SUBMIT_XPATH = "//*[@id='login-form']/div[3]/div/div/div/div/div/button[1]"
##Used just to login and take a screenshot
class LoginPage(BasePage):
    def open(self) -> None:
        self.go(self.cfg.BASE_URL)
    
    def fill_username(self, username: str) -> None:
        self.type_xpath(USERNAME_XPATH, username)
        
    def fill_password(self, password: str) -> None:
        self.type_xpath(PASSWORD_XPATH, password)
        
    def submit(self) -> None:
        self.click_xpath(SUBMIT_XPATH)
        
    def _save_screenshot(self, directory:str | None = None) -> str:
        directory = directory or os.getenv("SCREENSHOT_DIR") or os.path.join(os.getcwd(), "screenshots")
        os.makedirs(directory, exist_ok = True)
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(directory, f"login_{ts}.png")
        self.driver.save_screenshot(path)
        return path
        
    def login(self, username: str, password: str, screenshot_dir: str | None = None) -> str:
        self.open()
        self.fill_username(username)
        self.fill_password(password)
        self.submit()
        
        time.sleep(5)
        return self._save_screenshot(screenshot_dir)
    
    def login_with_env(self, screenshot_dir: str | None = None) -> str:
        return self.login(self.cfg.USERNAME, self.cfg.PASSWORD, screenshot_dir=screenshot_dir)
    