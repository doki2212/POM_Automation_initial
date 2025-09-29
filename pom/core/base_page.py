from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self,driver: WebDriver,cfg):
        self.driver = driver
        self.cfg = cfg
        self.wait = WebDriverWait(driver, cfg.EXPLICIT_WAIT)
        
    def go(self,url: str) -> None:
        self.driver.get(url)
        
    ### Wait helpers
    ##Wait until element exists in DOM
    def find_xpath(self, xpath: str, timeout: Optional[int] = None):
        w = WebDriverWait(self.driver, timeout or self.cfg.EXPLICIT_WAIT)
        return w.until(EC.presence_of_element_located((By.XPATH, xpath)))
    
    ##Element is visible
    def visible_xpath(self, xpath: str, timeout: Optional[int] = None):
        w = WebDriverWait(self.driver, timeout or self.cfg.EXPLICIT_WAIT)
        return w.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    
    ##Waiting until an element is clickable
    def clickable_xpath(self, xpath:str, timeout: Optional[int] = None):
        w = WebDriverWait(self.driver, timeout or self.cfg.EXPLICIT_WAIT)
        return w.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    
    ###interactions
    ##Clicking the element
    def click_xpath(self, xpath:str, timeout: Optional[int] = None) -> None:
        self.clickable_xpath(xpath, timeout).click()
        
    ##Type them sheez
    def type_xpath(self, xpath: str, text: str, clear: bool = True, timeout: Optional[int] = None) -> None:
        el = self.visible_xpath(xpath, timeout)
        if clear:
            el.clear()
        el.send_keys(text)    
        
    ##Returning texts of elements
    def get_text(self, xpath: str, timeout: Optional[int] = None) -> str:
        return self.visible_xpath(xpath, timeout).text.strip()
    
    ##Read Attributes
    def get_attr(self, xpath: str, name: str, timeout: Optional[int] = None):
        return self.find_xpath(xpath, timeout).get_attribute(name)
    
    ##Selecting dropdown menus
    def select_by_text(self, xpath: str, text: str, timeout: Optional[int] = None) -> None:
        el = self.visible_xpath(xpath, timeout)
        Select(el).select_by_visible_text(text)

    def select_by_value(self, xpath: str, value: str, timeout: Optional[int] = None) -> None:
        el = self.visible_xpath(xpath, timeout)
        Select(el).select_by_value(value)
    ##JS Click, JS == JavaScript, shithead
    def js_click(self, xpath: str, timeout: Optional[int] = None) -> None:
        el = self.visible_xpath(xpath, timeout)
        self.driver.execute_script("arguments[0].click()", el)
    ##Scrolling
    def scroll_into_view(self, xpath: str, block: str = "center", timeout: Optional[int] = None):
        el = self.find_xpath(xpath, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block: arguments[1]});", el, block)
        return el
    ##Wait for specific text
    def wait_for_text(self, xpath: str, text: str, timeout: Optional[int] = None) -> None:
        w = WebDriverWait(self.driver, timeout or self.cfg.EXPLICIT_WAIT)
        w.until(EC.text_to_be_present_in_element((By.XPATH, xpath), text))
    ##Waiting for overhead elements, if any to disappear
    def wait_gone(self, xpath: str, timeout: Optional[int] = None) -> None:
        w = WebDriverWait(self.driver, timeout or self.cfg.EXPLICIT_WAIT)
        w.until(EC.invisibility_of_element_located((By.XPATH, xpath)))
    ##Existence check, presence of ET, pop-up bs
    def exists(self, xpath: str, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except Exception:
            return False
    ##IFRAME ANNOYANCE SWTICH, didn't think of this one
    def switch_to_frame(self, xpath: str, timeout: Optional[int] = None) -> None:
        el = self.find_xpath(xpath, timeout)
        self.driver.switch_to.frame(el)

    def switch_to_default(self) -> None:
        self.driver.switch_to.default_content()
    ##Clean up errors when iframe switching
    def in_frame(self,xpath: str, timeout: Optional[int] = None):
        page = self
        class _Ctx:
            def __enter__(self):
                self._el = page.find_xpath(xpath, timeout)
                page.driver.switch_to.frame(self._el)
                return self._el
            def __exit__(self, exc_type, exc, tb):
                page.driver.switch_to.default_content()
                
        return _Ctx()