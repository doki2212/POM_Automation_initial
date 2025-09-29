import time
from pom.pages.home_page import HomePage
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


MONITORING_TAB_XPATH = "//*[@id='root']/div/aside/div/div[2]/ul/li[12]/span/a"
MON_FILTER_TRIGGER_XPATH = "//*[@id='root']/div/div/main/div/div[1]/div[1]/div"
OPEN_SELECT_INPUT_CANDIDATES = [
    "//div[contains(@class,'ant-select') and contains(@class,'open')]//input",
    "//div[contains(@class,'ant-select-open')]//input",
    "//div[contains(@class,'ant-select-focused')]//input",
    "//div[contains(@class,'ant-select') and (contains(@class,'open') or contains(@class,'focused'))]//*[@contenteditable='true']",
    "//*[@contenteditable='true']",
]

MON_DOWNLOAD_CANDIDATES = [
    "//*[@id='root']/div/div/main/div/div[1]/div[2]/div/a/button",             # button (preferred)
    "//*[@id='root']/div/div/main/div/div[1]/div[2]/div/a/button/span/svg",    # the svg you gave
    "//*[@id='root']/div/div/main/div/div[1]/div[2]//button",                  # any button in that block
]

#BELL_CANDIDATES = [
    #"//*[@id='root']/div/div/header/div/div[2]/div[1]/span",     # parent
    #"//*[@id='root']/div/div/header/div/div[2]/div[1]/span/svg", # child
#]

class Opt04MonitoringSummaryFlow:
    Name = "04 - Monitoring Summary"

    def __init__(self, driver, cfg):
        self.driver = driver
        self.cfg = cfg
        self.page = HomePage(driver, cfg)

    def run(self) -> bool:
        p = self.page
        self.driver.switch_to.default_content()

        # Try visible → normal click → scroll → JS click
        try:
            p.visible_xpath(MONITORING_TAB_XPATH, timeout=self.cfg.EXPLICIT_WAIT)
            p.click_xpath(MONITORING_TAB_XPATH, timeout=self.cfg.EXPLICIT_WAIT)
        except Exception:
            try:
                p.scroll_into_view(MONITORING_TAB_XPATH)
            except Exception:
                pass
            try:
                p.js_click(MONITORING_TAB_XPATH, timeout=self.cfg.EXPLICIT_WAIT)
            except Exception:
                print("[opt4] Could not click Monitoring Summary tab.")
                return False
            
        try:
            filter_text = input("Enter monitoring filter text: ").strip()
        except EOFError:
            filter_text = ""

        if not filter_text:
            print("[opt4] No filter text entered. Aborting.")
            return False
    
        if not self._robust_click(MON_FILTER_TRIGGER_XPATH):
            print("[opt4] Could not focus monitoring filter control")
            return False

        if not self._type_into_open_select(MON_FILTER_TRIGGER_XPATH, filter_text):
            print("[opt4] Failed to type into monitoring filter control")
            return False    
        
        dwn_btn_xp = self._first_clickable(MON_DOWNLOAD_CANDIDATES, timeout=self.cfg.EXPLICIT_WAIT)
        if not dwn_btn_xp or not self._robust_click(dwn_btn_xp):
            print("[opt4] Download button not clickable")
            return False   
        
        time.sleep(2)
        
        #self.driver.switch_to.default_content()  # just to be safe
        #bell_xp = self._first_clickable(BELL_CANDIDATES, timeout=self.cfg.EXPLICIT_WAIT)
        #if not bell_xp or not self._robust_click(bell_xp):
            #print("[opt4] Notification bell not clickable")
            #return False 

        time.sleep(7)  # small load wait
        return True
    
    
    ### HELPERS
    def _wait_any(self, xpaths, timeout):
        last = None
        for xp in xpaths:
            try:
                self.page.visible_xpath(xp, timeout=timeout)
                return xp
            except Exception as e:
                last = e
        raise last if last else TimeoutException("No panel became visible")

    def _first_visible(self, candidates, in_iframes: bool) -> str | None:
        for xp in candidates:
            if self._visible(xp):
                return xp
        if not in_iframes:
            return None
        frames = self.driver.find_elements(By.XPATH, "//iframe|//frame")
        for idx, fr in enumerate(frames):
            try:
                self.driver.switch_to.frame(fr)
                for xp in candidates:
                    if self._visible(xp):
                        return f"frame[{idx}]::{xp}"
            except Exception:
                pass
            finally:
                self.driver.switch_to.default_content()
        return None

    def _visible(self, xpath: str) -> bool:
        try:
            self.page.visible_xpath(xpath, timeout=2)
            return True
        except Exception:
            return False

    def _robust_click(self, target: str) -> bool:
        # If target is "frame[i]::xpath", switch in, click, switch back
        if target.startswith("frame["):
            idx = int(target.split("]::")[0].split("[")[1])
            xp  = target.split("]::", 1)[1]
            try:
                fr = self.driver.find_elements("xpath", "//iframe|//frame")[idx]
            except Exception:
                return False
            try:
                self.driver.switch_to.frame(fr)
                return self._click_now(xp)
            finally:
                self.driver.switch_to.default_content()
        else:
            return self._click_now(target)

    def _click_now(self, xpath: str) -> bool:
        p = self.page
        try:
            p.click_xpath(xpath, timeout=self.cfg.EXPLICIT_WAIT)
            return True
        except (TimeoutException, StaleElementReferenceException, Exception):
            try: p.scroll_into_view(xpath)
            except Exception: pass
            try:
                p.js_click(xpath, timeout=self.cfg.EXPLICIT_WAIT)
                return True
            except Exception:
                return False
            
    def _first_clickable(self, candidates, timeout: int) -> str | None:
        for xp in candidates:
            try:
                self.page.clickable_xpath(xp,timeout = timeout)
                return xp
            except Exception:
                continue
        return None
    
    def _type_into_open_select(self, trigger_xpath: str, text: str) -> bool:
        p = self.page
    # ensure it’s on screen and focused
        try:
            p.scroll_into_view(trigger_xpath)
        except Exception:
            pass
        if not self._robust_click(trigger_xpath):
            return False

        # tiny pause for the dropdown/input to mount
        time.sleep(0.2)

        # try to locate the live inner input of the open select
        input_xp = self._first_clickable(OPEN_SELECT_INPUT_CANDIDATES, timeout=5)
        el = None
        if input_xp:
            try:
                el = p.visible_xpath(input_xp, timeout=5)
            except Exception:
                el = None

        # fallback to active element if we didn’t find one by xpath
        if el is None:
            try:
                el = self.driver.switch_to.active_element
            except Exception:
                el = None

        if el is None:
            return False

        # clear any existing value
        try:
            el.clear()
        except Exception:
            try:
                el.send_keys(Keys.CONTROL, "a"); el.send_keys(Keys.BACKSPACE)
            except Exception:
                try:
                    el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.BACKSPACE)
                except Exception:
                    pass

        # type and commit
        try:
            el.send_keys(text)
            el.send_keys(Keys.ENTER)
            return True
        except Exception:
            return False
